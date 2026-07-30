"""SemanticCategory ORM model — user-defined domain categories for column mapping."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from api.database import Base


class SemanticCategory(Base):
    """A named category used to classify dataset columns in semantic mappings.

    The built-in defaults (vitals, labs, demographics, identifiers, meta) are
    seeded automatically on first startup.  Users can add, rename, and delete
    their own categories through the API.
    """

    __tablename__ = "semantic_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier for the category.",
    )
    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        comment="Short machine-friendly key used in semantic_mappings JSONB (e.g. 'vitals').",
    )
    label: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="Human-readable display label (e.g. 'Clinical / Vitals').",
    )
    color: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="Optional CSS color token or hex code for UI badge colouring.",
    )
    description: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True,
        comment="Optional description of what this category represents.",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,
        default=0,
        comment="Display order for lists and dropdowns (lower = first).",
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
        return f"<SemanticCategory {self.name!r} label={self.label!r}>"


# ── Default categories seeded on first startup ─────────────────────────────

DEFAULT_CATEGORIES: list[dict] = [
    {"name": "vitals",       "label": "Clinical / Vitals",  "color": "#3b82f6", "sort_order": 0,
     "description": "Physiological measurements such as blood pressure, heart rate, and respiration."},
    {"name": "labs",         "label": "Lab Tests",           "color": "#10b981", "sort_order": 1,
     "description": "Laboratory test results including blood work, urinalysis, and other assays."},
    {"name": "demographics", "label": "Demographics",        "color": "#8b5cf6", "sort_order": 2,
     "description": "Patient demographic attributes such as age, sex, and ethnicity."},
    {"name": "identifiers",  "label": "Identifiers",         "color": "#f59e0b", "sort_order": 3,
     "description": "Unique record identifiers, patient IDs, and reference keys."},
    {"name": "meta",         "label": "Metadata",            "color": "#6b7280", "sort_order": 4,
     "description": "Administrative and provenance fields such as import batch, timestamps, and audit trails."},
]
