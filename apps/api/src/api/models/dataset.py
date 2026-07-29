"""Dataset ORM model — uploaded datasets with processing metadata."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from api.database import Base

if TYPE_CHECKING:
    pass


class DatasetStatus(str, PyEnum):
    """Lifecycle of an uploaded dataset."""

    UPLOADING = "uploading"
    PROCESSING = "processing"
    PROFILING = "profiling"
    PROFILED = "profiled"
    SEMANTIC_REVIEW = "semantic_review"
    READY = "ready"
    ERROR = "error"


class Dataset(Base):
    """An uploaded dataset file with processing metadata."""

    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Original filename as uploaded by the user.",
    )
    storage_filename: Mapped[str] = mapped_column(
        String(255), nullable=False,
        comment="Unique filename on disk (to avoid collisions).",
    )
    filepath: Mapped[str] = mapped_column(
        String(1024), nullable=False,
        comment="Absolute path to the file on disk.",
    )
    file_size: Mapped[int | None] = mapped_column(
        Integer(), nullable=True,
        comment="File size in bytes.",
    )
    mime_type: Mapped[str] = mapped_column(
        String(128), nullable=False,
        comment="MIME type (e.g. text/csv, application/json).",
    )
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus, name="dataset_status"),
        nullable=False,
        default=DatasetStatus.UPLOADING,
        comment="Current processing status.",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text(), nullable=True,
        comment="Error message if processing failed.",
    )
    rows: Mapped[int | None] = mapped_column(
        Integer(), nullable=True,
        comment="Number of rows (populated after processing).",
    )
    columns: Mapped[int | None] = mapped_column(
        Integer(), nullable=True,
        comment="Number of columns (populated after processing).",
    )
    columns_info: Mapped[dict | None] = mapped_column(
        JSONB(), nullable=True,
        comment="Column metadata: name, dtype, null count, unique count.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<Dataset {self.id!r} file={self.original_filename!r}"
            f" status={self.status.value!r}>"
        )
