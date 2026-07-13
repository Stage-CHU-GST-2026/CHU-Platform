"""Chat and session endpoints."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage
from sse_starlette.sse import EventSourceResponse

from api.schemas.chat import (
    ChatNewResponse,
    ChatRequest,
    ErrorResponse,
    HistoryItem,
    HistoryResponse,
)
from api.services.session import SessionManager
from tools.visualization.visualization import CHARTS_DIR

router = APIRouter(prefix="/chat", tags=["chat"])
sessions = SessionManager()

# Ensure charts directory exists and mount it for static file serving.
# The router exposes it at /api/v1/charts/<filename>.
os.makedirs(CHARTS_DIR, exist_ok=True)
charts_static = StaticFiles(directory=CHARTS_DIR)


@router.post("/new", response_model=ChatNewResponse)
async def new_chat():
    """Start a fresh conversation."""
    thread_id = sessions.get_or_create()
    return ChatNewResponse(thread_id=thread_id)


@router.post("")
async def chat(request: ChatRequest):
    """Send a message and stream the response via SSE."""
    thread_id = sessions.get_or_create(request.thread_id)
    service = sessions.get_agent(thread_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_stream():
        # 1) Emit thread_id so the client can persist it
        yield {"event": "thread_id", "data": thread_id}
        # 2) Stream tokens and chart images
        async for event_type, data in service.stream(
            message=request.message,
            thread_id=thread_id,
            dataset_path=request.dataset_path,
        ):
            yield {"event": event_type, "data": data}
        # 3) Signal completion
        yield {"event": "done", "data": ""}

    return EventSourceResponse(
        event_stream(),
        headers={"X-Accel-Buffering": "no"},
    )


@router.get("/{thread_id}/history", response_model=HistoryResponse)
async def get_history(thread_id: str):
    """Return message history for a thread."""
    service = sessions.get_agent(thread_id)
    if service is None:
        raise HTTPException(status_code=404, detail=ErrorResponse(
            detail="Thread not found").model_dump())

    agent = service.agent
    try:
        state = await agent.graph.aget_state({"configurable": {"thread_id": thread_id}})
    except Exception:
        raise HTTPException(status_code=500, detail=ErrorResponse(
            detail="Failed to retrieve state").model_dump())

    if not state or not state.values.get("messages"):
        return HistoryResponse(thread_id=thread_id, messages=[])

    messages = []
    for msg in state.values["messages"]:
        if isinstance(msg, HumanMessage):
            messages.append(HistoryItem(role="user", content=msg.content))
        elif isinstance(msg, AIMessage):
            messages.append(HistoryItem(role="assistant", content=msg.content))

    return HistoryResponse(thread_id=thread_id, messages=messages)


@router.delete("/{thread_id}")
async def delete_session(thread_id: str):
    """Delete a session and free its resources."""
    sessions.remove(thread_id)
    return {"detail": "Session deleted"}
