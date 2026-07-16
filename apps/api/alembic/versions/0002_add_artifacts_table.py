"""add artifacts table linked to conversations

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-16
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "artifacts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "filename",
            sa.String(255),
            nullable=False,
            comment="Original filename on disk.",
        ),
        sa.Column(
            "filepath",
            sa.String(512),
            nullable=False,
            comment="Absolute path to the file on disk.",
        ),
        sa.Column(
            "mime_type",
            sa.String(128),
            nullable=False,
            comment="MIME type (e.g. image/png).",
        ),
        sa.Column(
            "file_size",
            sa.Integer(),
            nullable=True,
            comment="File size in bytes.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("artifacts")
