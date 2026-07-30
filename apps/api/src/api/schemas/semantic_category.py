"""Pydantic schemas for semantic category management endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SemanticCategoryCreate(BaseModel):
    """Body for creating a new semantic category."""

    name: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[a-z0-9_-]+$",
        description="Short machine-friendly key (lowercase, no spaces). E.g. 'vitals'.",
    )
    label: str = Field(
        min_length=1,
        max_length=128,
        description="Human-readable display label shown in dropdowns.",
    )
    color: str | None = Field(
        default=None,
        max_length=32,
        description="Optional CSS color token or hex code for badge colouring.",
    )
    description: str | None = Field(
        default=None,
        description="Optional description of what this category represents.",
    )
    sort_order: int = Field(
        default=0,
        description="Display order (lower = shown first in dropdowns).",
    )


class SemanticCategoryUpdate(BaseModel):
    """Body for partially updating a semantic category (PATCH semantics)."""

    label: str | None = Field(default=None, max_length=128)
    color: str | None = Field(default=None, max_length=32)
    description: str | None = Field(default=None)
    sort_order: int | None = Field(default=None)


class SemanticCategoryResponse(BaseModel):
    """Full representation of a semantic category returned from the API."""

    id: uuid.UUID
    name: str
    label: str
    color: str | None
    description: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
