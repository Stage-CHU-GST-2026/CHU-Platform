"""Dataset management endpoints — upload, list, preview, statistics, delete.

Uploaded files are stored to ``apps/api/datasets/`` and processed in a
background asyncio task (pandas loading + column profiling) so the
upload endpoint returns immediately.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_db
from api.models.dataset import Dataset, DatasetStatus
from api.schemas.dataset import (
    ColumnInfo,
    DatasetDetail,
    DatasetPreview,
    DatasetStatistics,
    DatasetSummary,
    DatasetUploadResponse,
    PreviewRow,
)
from api.services.dataset_service import (
    compute_statistics,
    ensure_datasets_dir,
    guess_mime,
    preview_dataset,
    process_dataset,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])

ALLOWED_EXTENSIONS = {".csv", ".tsv", ".xlsx",
                      ".xls", ".parquet", ".json", ".feather"}
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB


# ── Helpers ───────────────────────────────────────────────────────────

def _ensure_allowed(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {allowed}",
        )


# ── Upload ────────────────────────────────────────────────────────────

@router.post("/upload", response_model=DatasetUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Upload a dataset file.

    The file is saved to disk and queued for background processing
    (loading + column profiling). Returns immediately with the
    dataset ID and a ``processing`` status.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    _ensure_allowed(file.filename)

    # Read content
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum is {MAX_UPLOAD_SIZE // (1024*1024)} MB.",
        )

    # Determine storage path (unique name to avoid collisions)
    p = Path(file.filename)
    stem = p.stem
    ext = p.suffix.lower()
    storage_name = f"{stem}_{uuid.uuid4().hex}{ext}"
    datasets_dir = ensure_datasets_dir()
    filepath = str(datasets_dir / storage_name)

    # Write file to disk
    with open(filepath, "wb") as f:
        f.write(content)

    mime_type = guess_mime(file.filename)

    # Create DB record
    dataset = Dataset(
        original_filename=file.filename,
        storage_filename=storage_name,
        filepath=filepath,
        file_size=len(content),
        mime_type=mime_type,
        status=DatasetStatus.UPLOADING,
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)

    # Schedule background processing
    background_tasks.add_task(process_dataset, dataset.id)

    return DatasetUploadResponse(
        id=dataset.id,
        original_filename=dataset.original_filename,
        status=DatasetStatus.UPLOADING,
        message="File uploaded — processing in background.",
    )


# ── List ──────────────────────────────────────────────────────────────

@router.get("", response_model=list[DatasetSummary])
async def list_datasets(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    status_filter: DatasetStatus | None = Query(
        default=None, alias="status",
        description="Filter by processing status.",
    ),
):
    """Return all datasets, most recently uploaded first."""
    stmt = (
        select(Dataset)
        .order_by(Dataset.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    if status_filter:
        stmt = stmt.where(Dataset.status == status_filter)

    result = await db.execute(stmt)
    datasets = result.scalars().all()
    return [
        DatasetSummary(
            id=d.id,
            original_filename=d.original_filename,
            file_size=d.file_size,
            mime_type=d.mime_type,
            status=d.status,
            rows=d.rows,
            columns=d.columns,
            error_message=d.error_message,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )
        for d in datasets
    ]


# ── Get single ────────────────────────────────────────────────────────

@router.get("/{dataset_id}", response_model=DatasetDetail)
async def get_dataset(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return full details for a single dataset."""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    columns_info = None
    if dataset.columns_info:
        columns_info = [
            ColumnInfo(**col) for col in dataset.columns_info
        ]

    return DatasetDetail(
        id=dataset.id,
        original_filename=dataset.original_filename,
        file_size=dataset.file_size,
        mime_type=dataset.mime_type,
        status=dataset.status,
        error_message=dataset.error_message,
        rows=dataset.rows,
        columns=dataset.columns,
        columns_info=columns_info,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
    )


# ── Delete ────────────────────────────────────────────────────────────

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a dataset and its file from disk."""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )

    # Remove file from disk
    if dataset.filepath and os.path.isfile(dataset.filepath):
        os.remove(dataset.filepath)

    await db.delete(dataset)
    await db.commit()


# ── Preview ───────────────────────────────────────────────────────────

@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
async def get_dataset_preview(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    n: int = Query(default=10, le=100,
                   description="Number of rows to preview."),
):
    """Preview the first N rows of a dataset."""
    result = await preview_dataset(dataset_id, n, db)
    if result is None:
        # Check if dataset exists
        check = await db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        ds = check.scalar_one_or_none()
        if ds is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found.",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataset is not ready (status: {ds.status.value}).",
        )

    return DatasetPreview(**result)


# ── Statistics ────────────────────────────────────────────────────────

@router.get("/{dataset_id}/statistics", response_model=DatasetStatistics)
async def get_dataset_statistics(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Compute and return basic statistics for a dataset."""
    stats = await compute_statistics(dataset_id, db)
    if stats is None:
        check = await db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        ds = check.scalar_one_or_none()
        if ds is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found.",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataset is not ready (status: {ds.status.value}).",
        )

    return DatasetStatistics(
        dataset_id=dataset_id,
        numeric_summary=stats["numeric_summary"] or None,
        missing_values=stats["missing_values"],
        column_types=stats["column_types"],
    )


# ── Column info ───────────────────────────────────────────────────────

@router.get("/{dataset_id}/columns", response_model=list[ColumnInfo])
async def get_dataset_columns(
    dataset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Return column metadata for a dataset."""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found.",
        )
    if dataset.columns_info is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Dataset is not ready (status: {dataset.status.value}).",
        )

    return [ColumnInfo(**col) for col in dataset.columns_info]
