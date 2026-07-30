"""add_semantic_and_context_fields

Revision ID: b72f300c49ea
Revises: 7d178e5e5c4a
Create Date: 2026-07-30 16:48:42.197117

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b72f300c49ea'
down_revision: Union[str, None] = '7d178e5e5c4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add semantic mapping and dataset context columns to the datasets table.

    All columns are nullable so existing rows are unaffected.
    """
    op.add_column('datasets', sa.Column(
        'semantic_mappings',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        comment='User-curated semantic concept mappings per column (column_name, mapped_concept, category, confidence, unit, is_custom).',
    ))
    op.add_column('datasets', sa.Column(
        'context_description',
        sa.Text(),
        nullable=True,
        comment='Free-form business context overview and purpose of the dataset.',
    ))
    op.add_column('datasets', sa.Column(
        'context_notes',
        sa.Text(),
        nullable=True,
        comment='Business rules, domain assumptions, and data quality notes.',
    ))
    op.add_column('datasets', sa.Column(
        'context_tags',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        comment='Keyword and domain tags for search discoverability.',
    ))


def downgrade() -> None:
    op.drop_column('datasets', 'context_tags')
    op.drop_column('datasets', 'context_notes')
    op.drop_column('datasets', 'context_description')
    op.drop_column('datasets', 'semantic_mappings')
