"""Pydantic schemas for dataset management endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────

class DatasetStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


# ── Column info ───────────────────────────────────────────────────────

class ColumnInfo(BaseModel):
    """Metadata about a single column."""

    name: str
    dtype: str
    null_count: int
    unique_count: int
    sample: str | None = None


# ── Semantic Mapping ──────────────────────────────────────────────────

class SemanticMappingItem(BaseModel):
    """A single column's semantic concept mapping."""

    column_name: str
    dtype: str
    mapped_concept: str
    category: str
    confidence: int = Field(default=0, ge=0, le=100)
    unit: str | None = None
    is_custom: bool = False


class SemanticMappingUpdate(BaseModel):
    """Request body for replacing all semantic mappings of a dataset."""

    mappings: list[SemanticMappingItem]


# ── Dataset Context ───────────────────────────────────────────────────

class DatasetContextResponse(BaseModel):
    """Context information for a dataset."""

    description: str | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)


class DatasetContextUpdate(BaseModel):
    """Partial update of dataset context fields (PATCH semantics)."""

    description: str | None = Field(default=None)
    notes: str | None = Field(default=None)
    tags: list[str] | None = Field(default=None)


# ── Responses ─────────────────────────────────────────────────────────

class DatasetSummary(BaseModel):
    """Lightweight summary for list endpoints."""

    id: uuid.UUID
    original_filename: str
    file_size: int | None
    mime_type: str
    status: DatasetStatus
    rows: int | None
    columns: int | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetDetail(BaseModel):
    """Full dataset detail including column metadata, semantic mappings, and context."""

    id: uuid.UUID
    original_filename: str
    file_size: int | None
    mime_type: str
    status: DatasetStatus
    error_message: str | None
    rows: int | None
    columns: int | None
    columns_info: list[ColumnInfo] | None
    # Semantic mapping
    semantic_mappings: list[SemanticMappingItem] | None = None
    # Dataset context
    context_description: str | None = None
    context_notes: str | None = None
    context_tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetUploadResponse(BaseModel):
    """Response after uploading a dataset."""

    id: uuid.UUID
    original_filename: str
    status: DatasetStatus
    message: str = "File uploaded — processing in background."

    model_config = {"from_attributes": True}


class PreviewRow(BaseModel):
    """A single preview row as column→value mapping."""

    row_number: int
    values: dict[str, str | int | float | bool | None]


class DatasetPreview(BaseModel):
    """Preview of the first N rows of a dataset."""

    dataset_id: uuid.UUID
    total_rows: int
    total_columns: int
    columns: list[str]
    rows: list[PreviewRow]


class DatasetStatistics(BaseModel):
    """Statistics computed for a dataset."""

    dataset_id: uuid.UUID
    numeric_summary: dict[str, dict[str, float]] | None = None
    missing_values: dict[str, int] | None = None
    column_types: dict[str, str] | None = None


# ── Request ───────────────────────────────────────────────────────────

class DatasetUpdateRequest(BaseModel):
    """Optional payload to update dataset metadata."""

    original_filename: str | None = Field(default=None, max_length=255)
