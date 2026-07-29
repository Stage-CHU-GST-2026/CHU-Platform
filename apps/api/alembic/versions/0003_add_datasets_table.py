"""add datasets table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type first
    dataset_status_enum = postgresql.ENUM(
        "uploading", "processing", "ready", "error",
        name="dataset_status",
    )
    dataset_status_enum.create(op.get_bind())

    op.create_table(
        "datasets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "original_filename",
            sa.String(255),
            nullable=False,
            comment="Original filename as uploaded by the user.",
        ),
        sa.Column(
            "storage_filename",
            sa.String(255),
            nullable=False,
            comment="Unique filename on disk (to avoid collisions).",
        ),
        sa.Column(
            "filepath",
            sa.String(1024),
            nullable=False,
            comment="Absolute path to the file on disk.",
        ),
        sa.Column(
            "file_size",
            sa.Integer(),
            nullable=True,
            comment="File size in bytes.",
        ),
        sa.Column(
            "mime_type",
            sa.String(128),
            nullable=False,
            comment="MIME type (e.g. text/csv, application/json).",
        ),
        sa.Column(
            "status",
            dataset_status_enum,
            nullable=False,
            server_default=sa.text("'uploading'"),
            comment="Current processing status.",
        ),
        sa.Column(
            "error_message",
            sa.Text(),
            nullable=True,
            comment="Error message if processing failed.",
        ),
        sa.Column(
            "rows",
            sa.Integer(),
            nullable=True,
            comment="Number of rows (populated after processing).",
        ),
        sa.Column(
            "columns",
            sa.Integer(),
            nullable=True,
            comment="Number of columns (populated after processing).",
        ),
        sa.Column(
            "columns_info",
            postgresql.JSONB(),
            nullable=True,
            comment="Column metadata: name, dtype, null count, unique count.",
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
    op.drop_table("datasets")
    # Drop the enum type
    dataset_status_enum = postgresql.ENUM(
        "uploading", "processing", "ready", "error",
        name="dataset_status",
    )
    dataset_status_enum.drop(op.get_bind())
