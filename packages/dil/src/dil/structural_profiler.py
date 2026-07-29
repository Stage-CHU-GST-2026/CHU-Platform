"""Deterministic structural profiler for datasets."""

from __future__ import annotations

import re
from typing import Any
import pandas as pd
import numpy as np

from dil.models import ColumnStructuralInfo, StructuralProfile


ID_REGEX = re.compile(r"(?:_|^)(?:id|code|num|no|pk|key|uuid|identifier)(?:_|$)", re.IGNORECASE)


def analyze_column(df: pd.DataFrame, col: str) -> ColumnStructuralInfo:
    """Perform detailed structural analysis on a single column."""
    series = df[col]
    total_rows = len(df)
    null_count = int(series.isna().sum())
    null_pct = round((null_count / total_rows * 100.0) if total_rows > 0 else 0.0, 2)
    
    non_null_series = series.dropna()
    unique_count = int(non_null_series.nunique())
    unique_pct = round((unique_count / total_rows * 100.0) if total_rows > 0 else 0.0, 2)
    
    sample_val = str(non_null_series.iloc[0]) if len(non_null_series) > 0 else None

    # Detect basic type classifications
    is_bool = pd.api.types.is_bool_dtype(series) or (
        unique_count <= 2 and set(non_null_series.astype(str).str.lower().unique()).issubset({"true", "false", "0", "1", "yes", "no", "y", "n", "t", "f"})
    )
    is_num = pd.api.types.is_numeric_dtype(series) and not is_bool
    is_dt = pd.api.types.is_datetime64_any_dtype(series)
    
    # Try parsing string series to datetime if column name hints date/time
    if not is_dt and not is_num and not is_bool and len(non_null_series) > 0:
        if any(k in col.lower() for k in ["date", "time", "timestamp", "created", "updated", "dob"]):
            try:
                pd.to_datetime(non_null_series.head(50), errors="raise")
                is_dt = True
            except Exception:
                pass

    is_cat = not is_num and not is_dt and not is_bool

    # Detect candidate primary keys / IDs
    is_candidate_id = False
    if total_rows > 0 and (unique_count == total_rows or (unique_pct >= 95.0 and ID_REGEX.search(col))):
        is_candidate_id = True

    stats: dict[str, Any] = {}
    if is_num and len(non_null_series) > 0:
        try:
            stats = {
                "min": float(non_null_series.min()) if not np.isnan(non_null_series.min()) else None,
                "max": float(non_null_series.max()) if not np.isnan(non_null_series.max()) else None,
                "mean": round(float(non_null_series.mean()), 4) if not np.isnan(non_null_series.mean()) else None,
                "std": round(float(non_null_series.std()), 4) if len(non_null_series) > 1 and not np.isnan(non_null_series.std()) else None,
                "median": float(non_null_series.median()) if not np.isnan(non_null_series.median()) else None,
                "q25": float(non_null_series.quantile(0.25)) if not np.isnan(non_null_series.quantile(0.25)) else None,
                "q75": float(non_null_series.quantile(0.75)) if not np.isnan(non_null_series.quantile(0.75)) else None,
            }
        except Exception:
            pass
    elif is_cat and len(non_null_series) > 0:
        val_counts = non_null_series.value_counts().head(5).to_dict()
        stats = {"top_values": {str(k): int(v) for k, v in val_counts.items()}}

    return ColumnStructuralInfo(
        name=str(col),
        dtype=str(series.dtype),
        null_count=null_count,
        null_percentage=null_pct,
        unique_count=unique_count,
        unique_percentage=unique_pct,
        sample=sample_val,
        is_numeric=is_num,
        is_categorical=is_cat,
        is_datetime=is_dt,
        is_boolean=is_bool,
        is_candidate_id=is_candidate_id,
        stats=stats,
    )


def generate_structural_profile(df: pd.DataFrame) -> StructuralProfile:
    """Generate structural profile for a DataFrame."""
    total_rows = len(df)
    total_cols = len(df.columns)
    memory_mb = round(float(df.memory_usage(deep=True).sum()) / (1024 * 1024), 3)

    duplicate_rows = int(df.duplicated().sum())
    duplicate_pct = round((duplicate_rows / total_rows * 100.0) if total_rows > 0 else 0.0, 2)

    col_infos = [analyze_column(df, col) for col in df.columns]

    candidate_ids = [c.name for c in col_infos if c.is_candidate_id]
    datetime_cols = [c.name for c in col_infos if c.is_datetime]
    numeric_cols = [c.name for c in col_infos if c.is_numeric]
    categorical_cols = [c.name for c in col_infos if c.is_categorical]
    boolean_cols = [c.name for c in col_infos if c.is_boolean]

    return StructuralProfile(
        row_count=total_rows,
        column_count=total_cols,
        memory_mb=memory_mb,
        duplicate_rows=duplicate_rows,
        duplicate_percentage=duplicate_pct,
        columns=col_infos,
        candidate_ids=candidate_ids,
        datetime_columns=datetime_cols,
        numeric_columns=numeric_cols,
        categorical_columns=categorical_cols,
        boolean_columns=boolean_cols,
    )
