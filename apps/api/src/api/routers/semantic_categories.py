"""Semantic category management endpoints — CRUD for user-defined mapping categories.

Categories are stored in the ``semantic_categories`` table and used as the
domain buckets when assigning columns in the Semantic Mapping UI.

The five built-in defaults (vitals, labs, demographics, identifiers, meta) are
seeded automatically on first startup via the lifespan hook in ``main.py``.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models.semantic_category import SemanticCategory
from api.schemas.semantic_category import (
    SemanticCategoryCreate,
    SemanticCategoryResponse,
    SemanticCategoryUpdate,
)

router = APIRouter(prefix="/semantic-categories", tags=["semantic-categories"])


# ── Helpers ───────────────────────────────────────────────────────────

async def _get_category_or_404(cat_id: uuid.UUID, db: AsyncSession) -> SemanticCategory:
    result = await db.execute(
        select(SemanticCategory).where(SemanticCategory.id == cat_id)
    )
    cat = result.scalar_one_or_none()
    if cat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Semantic category not found.",
        )
    return cat


# ── List ──────────────────────────────────────────────────────────────

@router.get("", response_model=list[SemanticCategoryResponse])
async def list_semantic_categories(
    db: AsyncSession = Depends(get_db),
):
    """Return all semantic categories ordered by sort_order then name."""
    result = await db.execute(
        select(SemanticCategory).order_by(
            SemanticCategory.sort_order.asc(),
            SemanticCategory.name.asc(),
        )
    )
    return result.scalars().all()


# ── Create ────────────────────────────────────────────────────────────

@router.post("", response_model=SemanticCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_semantic_category(
    payload: SemanticCategoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new semantic category.

    The ``name`` must be unique (case-sensitive) across all categories.
    """
    # Check for name collision
    existing = await db.execute(
        select(SemanticCategory).where(SemanticCategory.name == payload.name)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A semantic category with name '{payload.name}' already exists.",
        )

    cat = SemanticCategory(
        name=payload.name,
        label=payload.label,
        color=payload.color,
        description=payload.description,
        sort_order=payload.sort_order,
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


# ── Get single ────────────────────────────────────────────────────────

@router.get("/{category_id}", response_model=SemanticCategoryResponse)
async def get_semantic_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return a single semantic category by ID."""
    return await _get_category_or_404(category_id, db)


# ── Update ────────────────────────────────────────────────────────────

@router.patch("/{category_id}", response_model=SemanticCategoryResponse)
async def update_semantic_category(
    category_id: uuid.UUID,
    payload: SemanticCategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Partially update a semantic category (PATCH semantics).

    Only fields present in the request body are changed; omitted fields
    retain their current values.  The ``name`` field cannot be changed
    after creation to avoid breaking existing semantic_mappings references.
    """
    cat = await _get_category_or_404(category_id, db)

    if payload.label is not None:
        cat.label = payload.label
    if payload.color is not None:
        cat.color = payload.color
    if payload.description is not None:
        cat.description = payload.description
    if payload.sort_order is not None:
        cat.sort_order = payload.sort_order

    await db.commit()
    await db.refresh(cat)
    return cat


# ── Delete ────────────────────────────────────────────────────────────

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_semantic_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a semantic category.

    Note: existing semantic_mappings JSONB entries that reference this
    category's ``name`` are not automatically updated — callers should
    re-assign those rows before deleting.
    """
    cat = await _get_category_or_404(category_id, db)
    await db.delete(cat)
    await db.commit()
