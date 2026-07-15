"""Conversation CRUD endpoints — backed by PostgreSQL."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse

from api.database import AsyncSessionLocal, get_db
from api.models.conversation import Conversation, Message
from api.schemas.chat import ConversationChatRequest
from api.schemas.conversation import (
    ConversationDetail,
    ConversationSummary,
    CreateConversationRequest,
    UpdateConversationRequest,
)
from api.services.session import SessionManager

router = APIRouter(prefix="/conversations", tags=["conversations"])
sessions = SessionManager()


# ── List ──────────────────────────────────────────────────────────────

@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """Return all conversations, most recently updated first."""
    # Subquery: count messages per conversation
    subq = (
        select(Message.conversation_id, func.count(Message.id).label("cnt"))
        .group_by(Message.conversation_id)
        .subquery()
    )

    stmt = (
        select(Conversation, subq.c.cnt)
        .outerjoin(subq, Conversation.id == subq.c.conversation_id)
        .order_by(Conversation.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )

    rows = await db.execute(stmt)
    return [
        ConversationSummary(
            id=conv.id,
            title=conv.title,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=count or 0,
        )
        for conv, count in rows
    ]


# ── Get single ────────────────────────────────────────────────────────

@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return a single conversation with all its messages."""
    stmt = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    return conv


# ── Create ────────────────────────────────────────────────────────────

@router.post("", response_model=ConversationDetail, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: CreateConversationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new empty conversation."""
    conv = Conversation(title=body.title)
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[],
    )


# ── Update title ──────────────────────────────────────────────────────

@router.patch("/{conversation_id}", response_model=ConversationDetail)
async def update_conversation(
    conversation_id: uuid.UUID,
    body: UpdateConversationRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update a conversation's title."""
    stmt = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    if body.title is not None:
        conv.title = body.title
    await db.flush()
    # Construct response manually to avoid lazy-load during serialization
    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageItem.model_validate(m) for m in conv.messages],
    )


# ── Delete ────────────────────────────────────────────────────────────

@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation and all its messages."""
    conv = await db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    await db.delete(conv)
    await db.flush()


# ── Chat inside a conversation ───────────────────────────────────────

@router.post("/{conversation_id}/chat")
async def chat_in_conversation(
    conversation_id: uuid.UUID,
    body: ConversationChatRequest,
):
    """Send a message inside a conversation and stream the response via SSE.

    The user message and the final assistant response are automatically
    persisted to the database. The conversation's UUID is used as the
    agent thread_id so LangGraph state is preserved across messages.
    """
    # Validate conversation exists
    async with AsyncSessionLocal() as db:
        conv = await db.get(Conversation, conversation_id)
        if conv is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

    # Get or create the agent session keyed on conversation_id
    thread_id = str(conversation_id)
    sessions.get_or_create(thread_id)
    service = sessions.get_agent(thread_id)
    if service is None:
        raise HTTPException(status_code=500, detail="Failed to create agent session")

    async def event_stream():
        async with AsyncSessionLocal() as db:
            # ── Save user message ──
            db.add(Message(
                conversation_id=conversation_id,
                role="user",
                content=body.message,
            ))
            await db.flush()

            # ── Auto-title on first message ──
            if not conv.title:
                msg_count = await db.scalar(
                    select(func.count(Message.id))
                    .where(Message.conversation_id == conversation_id)
                )
                if msg_count == 1:
                    title = body.message[:80]
                    if len(body.message) > 80:
                        title += "…"
                    conv.title = title

            await db.commit()

        # ── Emit thread_id ──
        yield {"event": "thread_id", "data": thread_id}

        # ── Stream agent tokens & collect chart URLs ──
        assistant_content = ""
        chart_urls: list[str] = []
        async for event_type, data in service.stream(
            message=body.message,
            thread_id=thread_id,
            dataset_path=body.dataset_path,
        ):
            if event_type == "token":
                assistant_content += str(data)
            elif event_type == "image":
                chart_urls.append(str(data))
            yield {"event": event_type, "data": data}

        # ── Save assistant response (with chart URLs embedded) ──
        full_content = assistant_content
        if chart_urls:
            charts_md = "\n\n" + "\n".join(
                f"![chart]({url})" for url in chart_urls
            )
            full_content += charts_md

        async with AsyncSessionLocal() as db:
            db.add(Message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_content,
            ))
            await db.commit()

        yield {"event": "done", "data": ""}

    return EventSourceResponse(
        event_stream(),
        headers={"X-Accel-Buffering": "no"},
    )
