"""Request / response models for the chat API."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message.")
    thread_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Conversation thread ID. Omit to start a new conversation.",
    )
    dataset_path: str | None = Field(
        default=None,
        description="Path to the dataset. Prepended to the message.",
    )


class ChatNewResponse(BaseModel):
    thread_id: str
    message: str = "New conversation started."


class HistoryItem(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class HistoryResponse(BaseModel):
    thread_id: str
    messages: list[HistoryItem]


class ErrorResponse(BaseModel):
    detail: str
