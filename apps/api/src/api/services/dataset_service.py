"""Dataset service — file storage, background processing, and analysis.

Uploaded files are saved to a dedicated ``datasets/`` directory.
Processing (pandas loading, column profiling) runs in a background
asyncio task so the upload endpoint returns immediately.
"""

from __future__ import annotations

import asyncio
import mimetypes
import os
import uuid
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import get_datasets_abs_dir
from api.database import AsyncSessionLocal
from api.models.dataset import Dataset, DatasetStatus

# ── Storage directory ─────────────────────────────────────────────────

DATASETS_DIR = Path(get_datasets_abs_dir())


def ensure_datasets_dir() -> Path:
    """Create the datasets storage directory if it doesn't exist."""
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    return DATASETS_DIR


# ── Supported file types ──────────────────────────────────────────────

SUPPORTED_EXTENSIONS: dict[str, str] = {
    ".csv": "text/csv",
    ".tsv": "text/tab-separated-values",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".parquet": "application/octet-stream",
    ".json": "application/json",
    ".feather": "application/octet-stream",
}

_FALLBACK_ENCODINGS = ["latin-1", "cp1252", "iso-8859-15"]


def guess_mime(filename: str) -> str:
    """Guess MIME type from filename extension."""
    ext = Path(filename).suffix.lower()
    return SUPPORTED_EXTENSIONS.get(ext, mimetypes.guess_type(filename)[0] or "application/octet-stream")


# ── Background processing ─────────────────────────────────────────────

def _load_dataframe(filepath: str) -> pd.DataFrame:
    """Load a dataset into a pandas DataFrame (runs in executor thread)."""
    p = Path(filepath)
    ext = p.suffix.lower()

    if ext == ".csv":
        for enc in ["utf-8", *_FALLBACK_ENCODINGS]:
            try:
                return pd.read_csv(p, encoding=enc)
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        # Last-resort fallback
        return pd.read_csv(p, encoding="utf-8")
    elif ext == ".tsv":
        return pd.read_csv(p, sep="\t")
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(p)
    elif ext == ".parquet":
        return pd.read_parquet(p)
    elif ext == ".json":
        return pd.read_json(p)
    elif ext == ".feather":
        return pd.read_feather(p)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def _profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Extract column metadata from a DataFrame (runs in executor thread).

    Returns a dict suitable for storing in Dataset.columns_info (JSONB).
    """
    info = []
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        unique_count = int(df[col].nunique())
        sample = df[col].dropna().iloc[0] if null_count < len(df) else None
        sample_str = str(sample) if sample is not None else None
        info.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "null_count": null_count,
            "unique_count": unique_count,
            "sample": sample_str,
        })
    return info


async def process_dataset(dataset_id: uuid.UUID) -> None:
    """Background task: load dataset, profile columns, update status.

    Spawns CPU-bound pandas operations in a thread executor so the
    event loop is not blocked.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        dataset = result.scalar_one_or_none()
        if dataset is None:
            return

        try:
            # Mark as processing
            dataset.status = DatasetStatus.PROCESSING
            await db.commit()

            # Load & profile in executor (CPU-bound)
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(None, _load_dataframe, dataset.filepath)
            columns_info = await loop.run_in_executor(
                None, _profile_dataframe, df
            )

            # Update with results
            dataset.rows = len(df)
            dataset.columns = len(df.columns)
            dataset.columns_info = columns_info

            # Auto-seed semantic mappings if not already present.
            # Use the raw column name as the initial mapped_concept so the
            # UI always has rows to display immediately after processing.
            if dataset.semantic_mappings is None:
                dataset.semantic_mappings = [
                    {
                        "column_name": col["name"],
                        "dtype": col["dtype"],
                        "mapped_concept": col["name"],
                        "category": "meta",
                        "confidence": 0,
                        "unit": None,
                        "is_custom": False,
                    }
                    for col in columns_info
                ]

            dataset.status = DatasetStatus.READY
            await db.commit()

        except Exception as exc:
            dataset.status = DatasetStatus.ERROR
            dataset.error_message = f"{type(exc).__name__}: {exc}"
            await db.commit()


# ── Statistics (lightweight, runs inline in request) ──────────────────

async def compute_statistics(dataset_id: uuid.UUID, db: AsyncSession) -> dict[str, Any] | None:
    """Compute basic statistics for a ready dataset.

    Returns a dict with numeric_summary, missing_values, and column_types,
    or None if the dataset is not ready.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if dataset is None or dataset.status != DatasetStatus.READY:
        return None

    # Load the DataFrame in executor
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(None, _load_dataframe, dataset.filepath)

    # Numeric summary
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    numeric_summary: dict[str, dict[str, float]] = {}
    if numeric_cols:
        desc = df[numeric_cols].describe().to_dict()
        for col, stats in desc.items():
            numeric_summary[str(col)] = {k: float(v) for k, v in stats.items()}

    # Missing values per column
    missing_values: dict[str, int] = {
        str(col): int(df[col].isna().sum()) for col in df.columns
    }

    # Column types
    column_types: dict[str, str] = {
        str(col): str(df[col].dtype) for col in df.columns
    }

    return {
        "numeric_summary": numeric_summary,
        "missing_values": missing_values,
        "column_types": column_types,
    }


async def preview_dataset(
    dataset_id: uuid.UUID,
    n: int,
    db: AsyncSession,
) -> dict[str, Any] | None:
    """Return the first N rows of a dataset as a preview.

    Returns a dict with columns list and rows list, or None if not ready.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if dataset is None or dataset.status != DatasetStatus.READY:
        return None

    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(None, _load_dataframe, dataset.filepath)

    head = df.head(n)
    rows = []
    for idx, row in head.iterrows():
        values: dict[str, str | int | float | bool | None] = {}
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                values[col] = None
            elif isinstance(val, (int, float, bool)):
                values[col] = val
            else:
                values[col] = str(val)
        rows.append({"row_number": int(idx), "values": values})

    return {
        "dataset_id": str(dataset_id),
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "rows": rows,
    }
