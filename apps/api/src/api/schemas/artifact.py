"""Pydantic schemas for artifact CRUD endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ArtifactItem(BaseModel):
    """An artifact attached to a conversation."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    filename: str
    mime_type: str
    file_size: int | None
    url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ArtifactUploadResponse(BaseModel):
    """Response after uploading / registering an artifact."""

    id: uuid.UUID
    conversation_id: uuid.UUID
    filename: str
    url: str
    created_at: datetime

    model_config = {"from_attributes": True}
