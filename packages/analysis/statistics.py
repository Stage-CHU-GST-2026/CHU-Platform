"""Statistical operations — pure pandas, no AI dependencies."""

from __future__ import annotations

import io

import pandas as pd


def describe(df: pd.DataFrame, include_all: bool = False) -> str:
    """Return a formatted statistical description.

    Args:
        df: The DataFrame.
        include_all: If True, also describe categorical columns.

    Returns:
        Formatted string.
    """
    buf = io.StringIO()

    print("=== Numeric columns ===", file=buf)
    num_cols = df.select_dtypes(include="number").columns.tolist()
    if num_cols:
        print(df[num_cols].describe().to_string(), file=buf)
    else:
        print("(none)", file=buf)

    if include_all:
        print(file=buf)
        print("=== All columns (mixed types) ===", file=buf)
        print(df.describe(include="all").to_string(), file=buf)

    return buf.getvalue()


def quantiles(
    df: pd.DataFrame,
    column: str,
    probs: list[float] | None = None,
) -> dict[str, float]:
    """Compute quantiles for a numeric column.

    Args:
        df: The DataFrame.
        column: Column name.
        probs: List of probabilities. Defaults to [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99].

    Returns:
        Dict mapping probability label → value.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found.")
    probs = probs or [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
    vals = df[column].quantile(probs)
    return {f"{p:.0%}": round(float(v), 4) for p, v in zip(probs, vals)}


def correlation_matrix(df: pd.DataFrame, cols: list[str] | None = None) -> pd.DataFrame:
    """Compute correlation matrix for numeric columns.

    Args:
        df: The DataFrame.
        cols: Subset of columns. If None, uses all numeric columns.

    Returns:
        Correlation matrix as DataFrame.
    """
    numeric = df.select_dtypes(include="number")
    if cols:
        numeric = numeric[[c for c in cols if c in numeric.columns]]
    return numeric.corr()
