"""add dataset_intelligence_records table

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_intelligence_records",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
            comment="Foreign key linking to datasets table.",
        ),
        sa.Column(
            "structural_profile",
            postgresql.JSONB(),
            nullable=True,
            comment="Detailed structural profiling data.",
        ),
        sa.Column(
            "quality_profile",
            postgresql.JSONB(),
            nullable=True,
            comment="Data quality dimension scores and issues.",
        ),
        sa.Column(
            "readiness_score",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0.0"),
            comment="Overall readiness score (0-100).",
        ),
        sa.Column(
            "readiness_breakdown",
            postgresql.JSONB(),
            nullable=True,
            comment="Score breakdown across DIL dimensions.",
        ),
        sa.Column(
            "warnings",
            postgresql.JSONB(),
            nullable=True,
            comment="List of dataset quality/readiness warnings.",
        ),
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
            comment="Intelligence record version.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("dataset_intelligence_records")
