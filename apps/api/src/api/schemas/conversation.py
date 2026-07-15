"""Pydantic schemas for conversation CRUD endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Nested ────────────────────────────────────────────────────────────

class MessageItem(BaseModel):
    """A single message in a conversation."""

    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Responses ─────────────────────────────────────────────────────────

class ConversationSummary(BaseModel):
    """Lightweight summary for list endpoints."""

    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    message_count: int

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    """Full conversation with messages."""

    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageItem]

    model_config = {"from_attributes": True}


# ── Requests ──────────────────────────────────────────────────────────

class CreateConversationRequest(BaseModel):
    """Payload for creating a new conversation."""

    title: str | None = Field(
        default=None, max_length=255,
        description="Optional title for the conversation.",
    )


class UpdateConversationRequest(BaseModel):
    """Payload for updating a conversation."""

    title: str | None = Field(
        default=None, max_length=255,
        description="New title for the conversation.",
    )
