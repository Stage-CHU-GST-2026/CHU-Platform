"""Conversation CRUD endpoints — backed by PostgreSQL."""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sse_starlette.sse import EventSourceResponse

from api.database import AsyncSessionLocal, get_db
from api.config import get_charts_abs_dir
from api.models.artifact import Artifact
from api.models.conversation import Conversation, Message
from api.schemas.artifact import ArtifactItem as ArtifactItemSchema
from api.schemas.chat import ConversationChatRequest
from api.schemas.conversation import (
    ConversationDetail,
    ConversationSummary,
    CreateConversationRequest,
    MessageItem,
    UpdateConversationRequest,
)
from api.services.session import session_manager
from api.schemas.artifact import ArtifactItem as ArtifactItemSchema

router = APIRouter(prefix="/conversations", tags=["conversations"])
sessions = session_manager


# ── Helpers ───────────────────────────────────────────────────────────

def _artifact_url(filename: str) -> str:
    return f"/api/v1/charts/{filename}"


def _fix_chart_urls(text: str) -> str:
    """Ensure chart image URLs have a leading slash so they resolve
    correctly in the browser regardless of the current page path.

    The LLM synthesizer sometimes strips the leading ``/`` from
    ``/api/v1/charts/…``, producing relative URLs like
    ``api/v1/charts/foo.png`` that break when the page URL is
    at a sub-path (e.g. ``/dashboard/conversation?id=…``).
    """
    return re.sub(
        r'\]\(api/v1/charts/',
        '](/api/v1/charts/',
        text,
    )


# ── List ──────────────────────────────────────────────────────────────

@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """Return all conversations, most recently updated first."""
    # Subquery: count messages per conversation
    msg_subq = (
        select(Message.conversation_id, func.count(Message.id).label("cnt"))
        .group_by(Message.conversation_id)
        .subquery()
    )
    # Subquery: count artifacts per conversation
    art_subq = (
        select(Artifact.conversation_id, func.count(Artifact.id).label("cnt"))
        .group_by(Artifact.conversation_id)
        .subquery()
    )

    stmt = (
        select(Conversation, msg_subq.c.cnt, art_subq.c.cnt)
        .outerjoin(msg_subq, Conversation.id == msg_subq.c.conversation_id)
        .outerjoin(art_subq, Conversation.id == art_subq.c.conversation_id)
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
            message_count=msg_count or 0,
            artifact_count=art_count or 0,
        )
        for conv, msg_count, art_count in rows
    ]


# ── Get single ────────────────────────────────────────────────────────

@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    include_artifacts: bool = Query(
        default=True,
        description="Include artifacts (generated plots) in the response.",
    ),
):
    """Return a single conversation with its messages and optionally artifacts."""
    stmt = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    if include_artifacts:
        stmt = stmt.options(selectinload(Conversation.artifacts))

    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()
    if conv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    artifacts = []
    if include_artifacts and conv.artifacts:
        artifacts = [
            ArtifactItemSchema(
                id=a.id,
                conversation_id=a.conversation_id,
                filename=a.filename,
                mime_type=a.mime_type,
                file_size=a.file_size,
                url=_artifact_url(a.filename),
                created_at=a.created_at,
            )
            for a in conv.artifacts
        ]

    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageItem.model_validate(m) for m in conv.messages],
        artifacts=artifacts,
    )


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
        artifacts=[],
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
    persisted to the database. Any generated charts / plots are saved as
    Artifact records linked to the conversation. The conversation's UUID
    is used as the agent thread_id so LangGraph state is preserved.
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
        raise HTTPException(
            status_code=500, detail="Failed to create agent session")

    async def event_stream():
        import os

        async with AsyncSessionLocal() as db:
            # ── Save user message ──
            db.add(Message(
                conversation_id=conversation_id,
                role="user",
                content=body.message,
            ))
            await db.commit()

        # ── Emit thread_id ──
        yield {"event": "thread_id", "data": thread_id}

        # ── Stream agent tokens & collect chart/artifact URLs ──
        assistant_content = ""
        chart_urls: list[str] = []
        artifact_metas: list[dict] = []
        plan_data: dict | None = None  # execution plan to persist
        async for event_type, data in service.stream(
            message=body.message,
            thread_id=thread_id,
            dataset_path=body.dataset_path,
        ):
            if event_type == "token":
                fixed = _fix_chart_urls(str(data))
                assistant_content += fixed
                data = fixed
            elif event_type == "image":
                url = str(data)
                if url not in chart_urls:
                    chart_urls.append(url)
            elif event_type == "chart_artifact":
                # Rich ChartArtifact payload — extract the api_url for persistence.
                # The image event is always emitted alongside this, but we guard
                # against duplication so double-registration cannot occur.
                try:
                    art_data = data if isinstance(
                        data, dict) else json.loads(str(data))
                    url = art_data.get("api_url", "")
                    if url and url not in chart_urls:
                        chart_urls.append(url)
                except Exception:
                    pass
            elif event_type == "artifact":
                meta = json.loads(str(data))
                artifact_metas.append(meta)
            elif event_type == "plan":
                # Capture the execution plan for persistence
                try:
                    plan_data = json.loads(str(data))
                except (json.JSONDecodeError, TypeError):
                    pass
            elif event_type == "step_evidence":
                continue
            elif event_type == "step_update":
                pass

            # Pass through all user-visible event types to the frontend
            yield {"event": event_type, "data": data}

        # ── Save assistant response (chart URLs already embedded above) ──
        # Double-check the full content for any chart URLs that were split
        # across token boundaries and missed by the per-token fix above.
        full_content = _fix_chart_urls(assistant_content)

        async with AsyncSessionLocal() as db:
            # Save assistant message
            db.add(Message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_content,
            ))

            # ── Persist chart files as Artifact records ──
            charts_abs_dir = get_charts_abs_dir()

            for chart_url in chart_urls:
                # chart_url is like "/api/v1/charts/foo.png"
                filename = os.path.basename(chart_url.rstrip("/"))
                if not filename:
                    continue
                filepath = os.path.join(charts_abs_dir, filename)
                file_size: int | None = None
                mime_type = "image/png"
                if filename.endswith(".svg"):
                    mime_type = "image/svg+xml"
                elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
                    mime_type = "image/jpeg"
                elif filename.endswith(".gif"):
                    mime_type = "image/gif"
                elif filename.endswith(".webp"):
                    mime_type = "image/webp"

                try:
                    file_size = os.path.getsize(filepath)
                except OSError:
                    pass

                db.add(Artifact(
                    conversation_id=conversation_id,
                    filename=filename,
                    filepath=filepath,
                    mime_type=mime_type,
                    file_size=file_size,
                ))

            # ── Persist plan artifacts as Artifact records ──
            artifact_ids: list[str] = []
            for meta in artifact_metas:
                filename = meta.get("filename", "")
                filepath = os.path.join(charts_abs_dir, filename)
                file_size = meta.get("file_size")
                art = Artifact(
                    conversation_id=conversation_id,
                    filename=filename,
                    filepath=filepath,
                    mime_type="text/markdown",
                    file_size=file_size,
                )
                db.add(art)
                await db.flush()
                await db.refresh(art)
                artifact_ids.append(str(art.id))

            # ── Persist execution plan as an Artifact ──────────────────
            if plan_data:
                plan_filename = f"plan_{conversation_id}.json"
                plan_filepath = os.path.join(charts_abs_dir, plan_filename)
                try:
                    with open(plan_filepath, "w") as f:
                        json.dump(plan_data, f)
                    plan_size = os.path.getsize(plan_filepath)
                except OSError:
                    plan_size = None

                db.add(Artifact(
                    conversation_id=conversation_id,
                    filename=plan_filename,
                    filepath=plan_filepath,
                    mime_type="application/vnd.chu.execution-plan+json",
                    file_size=plan_size,
                ))

            # ── Schedule title generation in the background ──
            if not conv.title:
                msg_count = await db.scalar(
                    select(func.count(Message.id))
                    .where(Message.conversation_id == conversation_id)
                )
                is_first = msg_count == 2
            else:
                is_first = False

            await db.commit()

        # ── Fire title generation in background (non-blocking) ──
        if is_first:
            asyncio.create_task(
                _auto_title(conversation_id, body.message)
            )

        yield {"event": "done", "data": ""}

    return EventSourceResponse(
        event_stream(),
        headers={"X-Accel-Buffering": "no"},
    )


async def _auto_title(conversation_id: uuid.UUID, user_message: str) -> None:
    """Generate a conversation title from the first user message via LLM.

    Runs in a background task so it never blocks the SSE stream.
    Re-checks that the title is still null before writing, so manual
    renames via ``PATCH /conversations/{id}`` are never overwritten.
    """
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage

        from api.config import settings

        llm = ChatOpenAI(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key or "sk-placeholder",
            model=settings.agent_model,
            temperature=0.0,
        )
        title_prompt = (
            "Generate a very short, concise title (maximum 5 words) for a conversation "
            "that starts with the message below. Respond with ONLY the title — "
            "no quotes, no extra punctuation, no explanation.\n\n"
            f"User message: {user_message}"
        )
        response = await llm.ainvoke(
            [HumanMessage(content=title_prompt)]
        )
        generated_title = (
            response.content.strip().strip('"').strip("'")[:255]
        )

        async with AsyncSessionLocal() as db:
            conv = await db.get(Conversation, conversation_id)
            # Only set if still null — respect manual renames
            if conv and not conv.title:
                conv.title = generated_title
                await db.commit()
    except Exception:
        # LLM unreachable or title generation failed — silently skip
        pass
