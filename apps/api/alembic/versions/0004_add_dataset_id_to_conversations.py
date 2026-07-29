"""add dataset_id FK to conversations table

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column(
            "dataset_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="Optional linked dataset for this conversation.",
        ),
    )
    op.create_foreign_key(
        "fk_conversations_dataset_id",
        "conversations",
        "datasets",
        ["dataset_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_conversations_dataset_id",
        "conversations",
        ["dataset_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_conversations_dataset_id")
    op.drop_constraint("fk_conversations_dataset_id",
                       "conversations", type_="foreignkey")
    op.drop_column("conversations", "dataset_id")
