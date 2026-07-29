"""Pydantic schemas for dataset management endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

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
    """Full dataset detail including column metadata."""

    id: uuid.UUID
    original_filename: str
    file_size: int | None
    mime_type: str
    status: DatasetStatus
    error_message: str | None
    rows: int | None
    columns: int | None
    columns_info: list[ColumnInfo] | None
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
