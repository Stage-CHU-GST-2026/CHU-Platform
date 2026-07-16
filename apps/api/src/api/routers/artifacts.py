"""Artifact endpoints — list, retrieve metadata, and serve generated files."""

from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.database import get_db
from api.models.artifact import Artifact
from api.models.conversation import Conversation
from api.schemas.artifact import ArtifactItem, ArtifactUploadResponse

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


# ── Helpers ───────────────────────────────────────────────────────────

def _build_url(filename: str) -> str:
    """Build the public URL for a chart file."""
    return f"/api/v1/charts/{filename}"


def _artifact_to_item(art: Artifact) -> ArtifactItem:
    return ArtifactItem(
        id=art.id,
        conversation_id=art.conversation_id,
        filename=art.filename,
        mime_type=art.mime_type,
        file_size=art.file_size,
        url=_build_url(art.filename),
        created_at=art.created_at,
    )


# ── List artifacts for a conversation ─────────────────────────────────

@router.get("", response_model=list[ArtifactItem])
async def list_artifacts(
    conversation_id: uuid.UUID = Query(...,
                                       description="Filter by conversation ID."),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Return all artifacts belonging to a conversation, newest first."""
    # Verify the conversation exists
    conv = await db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    stmt = (
        select(Artifact)
        .where(Artifact.conversation_id == conversation_id)
        .order_by(Artifact.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = await db.execute(stmt)
    artifacts = rows.scalars().all()
    return [_artifact_to_item(a) for a in artifacts]


# ── Get single artifact metadata ──────────────────────────────────────

@router.get("/{artifact_id}", response_model=ArtifactItem)
async def get_artifact(
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return metadata for a single artifact."""
    art = await db.get(Artifact, artifact_id)
    if art is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )
    return _artifact_to_item(art)


# ── Serve artifact file ───────────────────────────────────────────────

@router.get("/{artifact_id}/file")
async def serve_artifact_file(
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Download / view the actual artifact file.

    Returns the file inline with the correct Content-Type header so
    browsers display images directly.
    """
    art = await db.get(Artifact, artifact_id)
    if art is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact not found",
        )

    if not os.path.isfile(art.filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artifact file not found on disk",
        )

    return FileResponse(
        path=art.filepath,
        media_type=art.mime_type,
        filename=art.filename,
        headers={"Cache-Control": "public, max-age=3600"},
    )
