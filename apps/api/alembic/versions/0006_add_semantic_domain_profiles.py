"""add semantic_profile and domain_profile to dataset_intelligence_records

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE dataset_intelligence_records "
        "ADD COLUMN IF NOT EXISTS semantic_profile JSONB"
    )
    op.execute(
        "ALTER TABLE dataset_intelligence_records "
        "ADD COLUMN IF NOT EXISTS domain_profile JSONB"
    )


def downgrade() -> None:
    op.drop_column("dataset_intelligence_records", "domain_profile")
    op.drop_column("dataset_intelligence_records", "semantic_profile")
