"""Dataset profiling — shape, columns, dtypes, memory, nulls."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ColumnProfile:
    """Profile for a single column."""

    name: str
    dtype: str
    not_null: int
    nulls: int
    null_pct: float
    unique: int
    sample: str


@dataclass
class ProfileResult:
    """Structured result of dataset profiling."""

    rows: int
    columns: int
    memory_mb: float
    cols: list[ColumnProfile] = field(default_factory=list)

    def formatted(self) -> str:
        """Return a human-readable string."""
        import io

        buf = io.StringIO()
        print(f"Shape: {self.rows:,} rows × {self.columns} columns", file=buf)
        print(f"Memory: {self.memory_mb:.1f} MB", file=buf)
        print(file=buf)
        print(f"Columns ({len(self.cols)}):", file=buf)
        for c in self.cols:
            print(
                f"  • {c.name:30s}  {c.dtype:12s}  "
                f"nulls={c.nulls:>6} ({c.null_pct:5.1f}%)  "
                f"uniq={c.unique:>6}  e.g. {c.sample}",
                file=buf,
            )
        return buf.getvalue()


def profile(df: pd.DataFrame) -> ProfileResult:
    """Build a ProfileResult from a DataFrame."""
    result = ProfileResult(
        rows=len(df),
        columns=len(df.columns),
        memory_mb=df.memory_usage(deep=True).sum() / 1024**2,
    )
    for col in df.columns:
        nulls = int(df[col].isna().sum())
        unique = int(df[col].nunique())
        sample = df[col].dropna(
        ).iloc[0] if unique > 0 and not df[col].dropna().empty else "—"
        result.cols.append(
            ColumnProfile(
                name=col,
                dtype=str(df[col].dtype),
                not_null=int(df[col].count()),
                nulls=nulls,
                null_pct=round(nulls / len(df) * 100, 1) if len(df) else 0.0,
                unique=unique,
                sample=repr(sample),
            )
        )
    return result
