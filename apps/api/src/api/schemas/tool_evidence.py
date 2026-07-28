"""Pydantic schemas for ToolEvidence."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolEvidenceItem(BaseModel):
    """Schema representing a single tool evidence record."""

    id: uuid.UUID
    message_id: int
    conversation_id: uuid.UUID
    step_id: int | None = None
    tool_name: str
    tool_call_id: str | None = None
    parameters: dict[str, Any] | None = None
    result: str = ""
    status: str = "success"
    execution_time_ms: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CreateToolEvidenceRequest(BaseModel):
    """Schema for creating tool evidence."""

    step_id: int | None = None
    tool_name: str
    tool_call_id: str | None = None
    parameters: dict[str, Any] | None = None
    result: str = ""
    status: str = "success"
    execution_time_ms: int | None = None
