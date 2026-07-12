"""AnalysisEngine — unified entry point for all dataset operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .profiler import ProfileResult, profile
from .statistics import correlation_matrix, describe, quantiles


class AnalysisEngine:
    """Executes analysis operations on datasets.

    Pure business logic — no LangChain, no OpenAI, no LangGraph.
    """

    def __init__(self) -> None:
        self._loaded: dict[str, pd.DataFrame] = {}

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    LOADERS: dict[str, Any] = {
        ".csv": lambda p, **kw: pd.read_csv(p, **kw),
        ".tsv": lambda p, **kw: pd.read_csv(p, sep="\t", **kw),
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".parquet": pd.read_parquet,
        ".json": pd.read_json,
        ".feather": pd.read_feather,
    }

    def load(self, path: str, **kwargs) -> pd.DataFrame:
        """Load a dataset, cache it, and return the DataFrame."""
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
        ext = p.suffix.lower()
        loader = self.LOADERS.get(ext)
        if loader is None:
            raise ValueError(
                f"Unsupported extension '{ext}'. "
                f"Supported: {', '.join(self.LOADERS)}"
            )
        df = loader(p, **kwargs)
        self._loaded[str(p)] = df
        return df

    def get(self, path: str) -> pd.DataFrame | None:
        """Return cached DataFrame if already loaded."""
        return self._loaded.get(str(Path(path).expanduser().resolve()))

    # ------------------------------------------------------------------
    # Profiling / inspection
    # ------------------------------------------------------------------

    def profile(self, df: pd.DataFrame) -> ProfileResult:
        """Return a structured profile of the dataset."""
        return profile(df)

    def describe(self, df: pd.DataFrame, include_all: bool = False) -> str:
        """Return a formatted statistical description of numeric columns."""
        return describe(df, include_all=include_all)

    def head(self, df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
        """Return the first n rows."""
        return df.head(min(n, 20))

    def column_info(self, df: pd.DataFrame, column: str) -> str:
        """Return detailed info for a single column."""
        if column not in df.columns:
            cols = ", ".join(df.columns[:20])
            return f"Column '{column}' not found. Available: {cols}"
        return _format_column_stats(df[column])

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def quantiles(self, df: pd.DataFrame, column: str, probs: list[float] | None = None) -> dict[str, float]:
        """Compute quantiles for a numeric column."""
        return quantiles(df, column, probs)

    def correlation(self, df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
        """Return a correlation matrix for numeric columns."""
        return correlation_matrix(df, cols)

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    def aggregate(
        self,
        df: pd.DataFrame,
        group_by: str | list[str],
        agg: str | dict[str, str],
        **kwargs,
    ) -> pd.DataFrame:
        """Group by column(s) and apply aggregation."""
        return df.groupby(group_by, **kwargs).agg(agg).reset_index()

    def filter_rows(self, df: pd.DataFrame, query: str) -> pd.DataFrame:
        """Filter rows using a pandas query expression."""
        return df.query(query).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Missing data
    # ------------------------------------------------------------------

    def missing_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a table of missing values per column."""
        summary = pd.DataFrame({
            "column": df.columns,
            "dtype": [str(d) for d in df.dtypes.values],
            "missing": df.isna().sum().values,
            "missing_pct": (df.isna().mean() * 100).values,
            "unique": df.nunique().values,
        })
        return summary.sort_values("missing", ascending=False).reset_index(drop=True)

    def drop_columns(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """Drop specified columns."""
        return df.drop(columns=columns, errors="ignore")

    # ------------------------------------------------------------------
    # Outliers
    # ------------------------------------------------------------------

    def detect_outliers_iqr(self, df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.DataFrame:
        """Return rows where the column value is an IQR outlier."""
        q1, q3 = df[column].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        return df[(df[column] < lower) | (df[column] > upper)].copy()


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _format_column_stats(col: pd.Series) -> str:
    """Build a human-readable string of column statistics."""
    import io

    buf = io.StringIO()
    print(f"Column : {col.name}", file=buf)
    print(f"Dtype  : {col.dtype}", file=buf)
    print(f"Count  : {col.count():,}", file=buf)
    print(
        f"Nulls  : {col.isna().sum():,}  ({col.isna().mean() * 100:.1f}%)", file=buf)
    print(f"Unique : {col.nunique():,}", file=buf)
    print(file=buf)

    if pd.api.types.is_numeric_dtype(col):
        print(f"Min    : {col.min()}", file=buf)
        print(f"Max    : {col.max()}", file=buf)
        print(f"Mean   : {col.mean():.4f}", file=buf)
        print(f"Median : {col.median():.4f}", file=buf)
        print(f"Std    : {col.std():.4f}", file=buf)
        print(file=buf)
        print("--- Quantiles ---", file=buf)
        for q in [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]:
            print(f"  {q:5.0%} : {col.quantile(q):.4f}", file=buf)
    else:
        print("--- Top values ---", file=buf)
        for val, cnt in col.value_counts().head(10).items():
            print(
                f"  {str(val):40s}  {cnt:>8,}  ({cnt / len(col) * 100:.1f}%)", file=buf)

    return buf.getvalue()
