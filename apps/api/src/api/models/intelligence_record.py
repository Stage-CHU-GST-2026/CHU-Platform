"""DatasetIntelligenceRecord ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base

if TYPE_CHECKING:
    from api.models.dataset import Dataset


class DatasetIntelligenceRecord(Base):
    """Persistent Dataset Intelligence Record for a dataset."""

    __tablename__ = "dataset_intelligence_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Foreign key linking to datasets table.",
    )
    structural_profile: Mapped[dict | None] = mapped_column(
        JSONB(), nullable=True,
        comment="Detailed structural profiling data.",
    )
    quality_profile: Mapped[dict | None] = mapped_column(
        JSONB(), nullable=True,
        comment="Data quality dimension scores and issues.",
    )
    semantic_profile: Mapped[dict | None] = mapped_column(
        JSONB(), nullable=True,
        comment="Semantic concept mappings, roles, and units.",
    )
    domain_profile: Mapped[dict | None] = mapped_column(
        JSONB(), nullable=True,
        comment="Dataset domain classification profile.",
    )
    readiness_score: Mapped[float] = mapped_column(
        Float(), default=0.0, nullable=False,
        comment="Overall readiness score (0-100).",
    )
    readiness_breakdown: Mapped[dict | None] = mapped_column(
        JSONB(), nullable=True,
        comment="Score breakdown across DIL dimensions.",
    )
    warnings: Mapped[list | None] = mapped_column(
        JSONB(), nullable=True,
        comment="List of dataset quality/readiness warnings.",
    )
    version: Mapped[int] = mapped_column(
        Integer(), default=1, nullable=False,
        comment="Intelligence record version.",
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

    dataset: Mapped[Dataset] = relationship("Dataset", backref="intelligence_record", uselist=False)

    def __repr__(self) -> str:
        return (
            f"<DatasetIntelligenceRecord dataset_id={self.dataset_id!r}"
            f" readiness={self.readiness_score:.1f}% version={self.version}>"
        )
