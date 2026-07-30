"""add_semantic_categories_table

Revision ID: 1dba1e84aff6
Revises: b72f300c49ea
Create Date: 2026-07-30 17:06:50.844111

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1dba1e84aff6'
down_revision: Union[str, None] = 'b72f300c49ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the semantic_categories table.

    Default rows (vitals, labs, demographics, identifiers, meta) are seeded
    at application startup via the lifespan hook, not in this migration, so
    that they can be managed through the API without re-running migrations.
    """
    op.create_table(
        'semantic_categories',
        sa.Column('id', sa.UUID(), nullable=False,
                  comment='Unique identifier for the category.'),
        sa.Column('name', sa.String(length=64), nullable=False,
                  comment="Short machine-friendly key (e.g. 'vitals')."),
        sa.Column('label', sa.String(length=128), nullable=False,
                  comment="Human-readable display label (e.g. 'Clinical / Vitals')."),
        sa.Column('color', sa.String(length=32), nullable=True,
                  comment='Optional CSS color token or hex code for badge colouring.'),
        sa.Column('description', sa.Text(), nullable=True,
                  comment='Optional description of what this category represents.'),
        sa.Column('sort_order', sa.Integer(), nullable=False,
                  comment='Display order (lower = first).'),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('semantic_categories_pkey')),
        sa.UniqueConstraint('name', name=op.f('semantic_categories_name_key')),
    )


def downgrade() -> None:
    op.drop_table('semantic_categories')
