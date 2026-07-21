"""AnalysisEngine — unified entry point for all dataset operations."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from .profiler import ProfileResult, profile
from .statistics import correlation_matrix, describe, quantiles


def _find_data_dir() -> Path | None:
    """Find a ``data/`` directory by walking up from CWD."""
    cwd = Path.cwd().resolve()
    for ancestor in [cwd] + list(cwd.parents):
        candidate = ancestor / "data"
        if candidate.is_dir():
            return candidate
    return None


def _list_datasets(data_dir: Path | None = None) -> list[Path]:
    """Return paths of supported dataset files in a given directory."""
    SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".xlsx",
                            ".xls", ".parquet", ".json", ".feather"}
    if data_dir is None:
        data_dir = _find_data_dir()
    if data_dir is None:
        return []
    return sorted(
        p for p in data_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )


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
        ".csv": lambda p, **kw: AnalysisEngine._load_csv_with_fallback(p, **kw),
        ".tsv": lambda p, **kw: AnalysisEngine._load_csv_with_fallback(p, sep="\t", **kw),
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".parquet": pd.read_parquet,
        ".json": pd.read_json,
        ".feather": pd.read_feather,
    }

    # Encodings to try when UTF-8 fails on text-based files
    _FALLBACK_ENCODINGS = ["latin-1", "cp1252", "iso-8859-15"]

    @staticmethod
    def _load_csv_with_fallback(path: Path, **kwargs: Any) -> pd.DataFrame:
        """Read a CSV, auto-detecting encoding and delimiter.

        Tries UTF-8 first, then common fallback encodings (latin-1, cp1252, …).
        When no explicit ``sep`` is given and comma-separated parsing fails,
        also tries ``;``, ``\\t`` and ``|`` as delimiters.
        """
        user_sep = "sep" in kwargs or "delimiter" in kwargs

        encodings = (
            [kwargs.pop("encoding")]
            if "encoding" in kwargs
            else ["utf-8", *AnalysisEngine._FALLBACK_ENCODINGS]
        )

        # First pass: try each encoding with the user-provided separator (default comma)
        for enc in encodings:
            try:
                return pd.read_csv(path, encoding=enc, **kwargs)
            except UnicodeDecodeError:
                continue
            except pd.errors.ParserError:
                # Encoding is fine but delimiter is wrong — break out to try other delimiters
                break

        # Second pass: try other delimiters if the user didn't specify one
        if not user_sep:
            for enc in encodings:
                for sep in (";", "\t", "|"):
                    try:
                        return pd.read_csv(path, encoding=enc, sep=sep, **kwargs)
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue

        # Last resort: let pandas raise the original error
        return pd.read_csv(path, encoding="utf-8", **kwargs)

    def load(self, path: str, **kwargs) -> pd.DataFrame:
        """Load a dataset, cache it, and return the DataFrame."""
        p = Path(path).expanduser().resolve()
        if not p.exists():
            # Build a helpful message listing available datasets
            available = _list_datasets()
            msg = f"File not found: {p}"
            if available:
                items = "\n".join(f"  - {d.name}" for d in available)
                msg += (
                    f"\n\nAvailable datasets in the data/ folder:\n{items}"
                    "\n\nUse the `list_datasets` tool to see all available datasets, "
                    "then call the desired tool with the correct path "
                    "(e.g. 'data/dataset_name.csv')."
                )
            raise FileNotFoundError(msg)
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
    # SQL
    # ------------------------------------------------------------------

    def _ensure_sql_registered(self) -> None:
        """Register all loaded DataFrames with the DuckDB connection."""
        self._sql_conn = duckdb.connect()  # in-memory, recreated each time
        for abs_path, df in self._loaded.items():
            table_name = Path(abs_path).stem.replace(".", "_").replace("-", "_")
            self._sql_conn.register(table_name, df)

    def sql_tables(self) -> str:
        """List all tables available for SQL querying (loaded datasets)."""
        self._ensure_sql_registered()
        tables = self._sql_conn.execute("SHOW TABLES").fetchall()
        if not tables:
            return (
                "No datasets loaded. Use `describe_dataset` or another tool "
                "first to load a dataset, then you can query it with SQL."
            )
        lines = ["Tables available for SQL queries:\n"]
        for (table_name,) in tables:
            # Resolve which file this table came from
            for abs_path in self._loaded:
                if Path(abs_path).stem.replace(".", "_").replace("-", "_") == table_name:
                    lines.append(
                        f"  📊 {table_name}  ←  {Path(abs_path).name}  "
                        f"({len(self._loaded[abs_path]):,} rows × "
                        f"{len(self._loaded[abs_path].columns)} cols)"
                    )
                    break
            else:
                lines.append(f"  📊 {table_name}")
        return "\n".join(lines)

    def sql_schema(self, table: str) -> str:
        """Return the schema (columns + types) for a registered table."""
        self._ensure_sql_registered()
        try:
            result = self._sql_conn.execute(
                f"DESCRIBE {table}"
            ).fetchall()
        except Exception as e:
            available = [Path(p).stem.replace(".", "_").replace("-", "_")
                         for p in self._loaded]
            return (
                f"Table '{table}' not found.\n"
                f"Available tables: {', '.join(available) if available else '(none)'}\n"
                f"Use `sql_tables` to list available tables.\n"
                f"Error: {e}"
            )
        lines = [f"Schema for table '{table}':\n"]
        lines.append(f"{'Column':30s} {'Type':15s} {'Nullable':>8}")
        lines.append("-" * 55)
        for col_name, col_type, nullable, *_ in result:
            lines.append(
                f"{col_name:30s} {col_type:15s} {str(nullable):>8}"
            )
        # Add row count
        count = self._sql_conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        lines.append(f"\nTotal rows: {count:,}")
        return "\n".join(lines)

    def sql_query(self, query: str) -> str:
        """Execute a SQL query against loaded datasets and return the result.

        The query can use any loaded dataset as a table. Table names are
        derived from filenames (dots/hyphens replaced with underscores).

        Returns the result as a formatted text table (max 50 rows).
        """
        self._ensure_sql_registered()
        try:
            result = self._sql_conn.execute(query)
            # Fetch up to 50 rows
            rows = result.fetchmany(50)
            if not rows:
                # For non-SELECT queries (CREATE, INSERT, etc.)
                return f"Query executed successfully.\n{result.description or ''}"

            col_names = [desc[0] for desc in result.description]
            buf = io.StringIO()

            # Build a simple text table
            # Calculate column widths
            col_widths = [len(name) for name in col_names]
            for row in rows:
                for i, val in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(val)))

            # Header
            header = " | ".join(
                name.ljust(col_widths[i]) for i, name in enumerate(col_names)
            )
            sep = "-+-".join("-" * w for w in col_widths)
            buf.write(header + "\n")
            buf.write(sep + "\n")

            # Rows
            for row in rows:
                buf.write(
                    " | ".join(
                        str(val).ljust(col_widths[i]) for i, val in enumerate(row)
                    )
                    + "\n"
                )

            # Check if there are more rows
            remaining = result.fetchone()
            if remaining is not None:
                buf.write(f"\n(Showing first 50 rows — query returned more results)")

            return buf.getvalue()
        except Exception as e:
            return f"SQL error: {e}"


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
