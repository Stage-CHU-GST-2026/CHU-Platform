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
        self._sql_history: list[dict[str, Any]] = []
        self._sql_views: set[str] = set()

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
            self._record_query(query, success=True)
            formatted = self._format_sql_result(result)
            return formatted
        except Exception as e:
            self._record_query(query, success=False)
            return f"SQL error: {e}"

    # ------------------------------------------------------------------
    # SQL – Data exploration
    # ------------------------------------------------------------------

    def sql_sample(self, table: str, n: int = 10) -> str:
        """Return a sample of N rows from a table."""
        self._ensure_sql_registered()
        try:
            result = self._sql_conn.execute(
                f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT {n}"
            )
            return self._format_sql_result(result, max_rows=n)
        except Exception as e:
            return f"SQL error: {e}"

    def sql_stats(self, table: str, columns: list[str] | None = None) -> str:
        """Compute basic statistics for numeric columns."""
        self._ensure_sql_registered()
        try:
            # Discover numeric columns if none specified
            if columns is None:
                schema = self._sql_conn.execute(f"DESCRIBE {table}").fetchall()
                numeric_types = {
                    "INTEGER", "BIGINT", "SMALLINT", "TINYINT", "HUGEINT",
                    "FLOAT", "DOUBLE", "DECIMAL", "REAL", "NUMERIC",
                }
                columns = [
                    col_name for col_name, col_type, *_ in schema
                    if any(t in col_type.upper() for t in numeric_types)
                ]
            if not columns:
                return f"No numeric columns found in table '{table}'."

            lines = [f"Statistics for numeric columns in '{table}':\n"]
            for col in columns:
                try:
                    stats = self._sql_conn.execute(f"""
                        SELECT
                            COUNT("{col}") AS count,
                            MIN("{col}") AS min,
                            MAX("{col}") AS max,
                            AVG("{col}") AS mean,
                            STDDEV("{col}") AS std,
                            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "{col}") AS q25,
                            PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY "{col}") AS median,
                            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "{col}") AS q75
                        FROM {table}
                        WHERE "{col}" IS NOT NULL
                    """).fetchone()
                    null_count = self._sql_conn.execute(
                        f'SELECT COUNT(*) FROM {table} WHERE "{col}" IS NULL'
                    ).fetchone()[0]
                    lines.append(f"  📊 {col}:")
                    lines.append(f"     count={stats[0]:,}  nulls={null_count:,}  "
                                 f"min={stats[1]}  max={stats[2]}")
                    lines.append(f"     mean={stats[3]:.4f}  std={stats[4]:.4f}  "
                                 f"Q25={stats[5]}  median={stats[6]}  Q75={stats[7]}")
                except Exception as e:
                    lines.append(f"  ⚠ {col}: error — {e}")
            return "\n".join(lines)
        except Exception as e:
            return f"SQL error: {e}"

    def sql_unique(self, table: str, column: str, limit: int = 20) -> str:
        """Get unique values and their frequencies for a column."""
        self._ensure_sql_registered()
        try:
            result = self._sql_conn.execute(f"""
                SELECT "{column}", COUNT(*) AS frequency,
                       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {table}), 2) AS pct
                FROM {table}
                GROUP BY "{column}"
                ORDER BY frequency DESC
                LIMIT {limit}
            """)
            rows = result.fetchall()
            if not rows:
                return f"Column '{column}' in table '{table}' is empty."
            total_unique = self._sql_conn.execute(
                f'SELECT COUNT(DISTINCT "{column}") FROM {table}'
            ).fetchone()[0]
            lines = [
                f"Unique values for '{column}' in '{table}':",
                f"Total distinct values: {total_unique}",
                f"\n{'Value':40s} {'Count':>10s} {'Percent':>8s}",
                "-" * 62,
            ]
            for val, cnt, pct in rows:
                val_str = str(val)[:38] if val is not None else "NULL"
                lines.append(f"{val_str:40s} {cnt:>10,} {pct:>7.1f}%")
            if total_unique > limit:
                lines.append(f"\n... showing top {limit} of {total_unique} values")
            return "\n".join(lines)
        except Exception as e:
            return f"SQL error: {e}"

    # ------------------------------------------------------------------
    # SQL – Query analysis & debugging
    # ------------------------------------------------------------------

    def sql_explain(self, query: str) -> str:
        """Show the execution plan for a query without running it."""
        self._ensure_sql_registered()
        try:
            result = self._sql_conn.execute(f"EXPLAIN {query}")
            plan_lines = [row[0] for row in result.fetchall()]
            return "Execution plan:\n\n" + "\n".join(plan_lines)
        except Exception as e:
            return f"EXPLAIN error: {e}"

    def sql_validate(self, query: str) -> str:
        """Validate SQL syntax without executing the query."""
        self._ensure_sql_registered()
        try:
            # Use EXPLAIN to check syntax without executing side effects
            self._sql_conn.execute(f"EXPLAIN {query}")
            return (
                "✅ SQL syntax is valid.\n\n"
                "Tip: Use `sql_explain` to see the execution plan."
            )
        except Exception as e:
            return f"❌ SQL validation failed: {e}"

    # ------------------------------------------------------------------
    # SQL – Data quality
    # ------------------------------------------------------------------

    def sql_nulls(self, table: str) -> str:
        """Check for NULL values across all columns in a table."""
        self._ensure_sql_registered()
        try:
            schema = self._sql_conn.execute(f"DESCRIBE {table}").fetchall()
            total_rows = self._sql_conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            lines = [
                f"NULL analysis for '{table}' ({total_rows:,} total rows):\n",
                f"{'Column':30s} {'Nulls':>8s} {'Null%':>7s} {'Status':>12s}",
                "-" * 62,
            ]
            for col_name, *_ in schema:
                null_count = self._sql_conn.execute(
                    f'SELECT COUNT(*) FROM {table} WHERE "{col_name}" IS NULL'
                ).fetchone()[0]
                null_pct = (null_count / total_rows * 100) if total_rows else 0
                if null_pct == 0:
                    status = "✅ Clean"
                elif null_pct < 5:
                    status = "⚠ Minor"
                elif null_pct < 20:
                    status = "⚠ Moderate"
                else:
                    status = "❌ Severe"
                lines.append(
                    f"{col_name:30s} {null_count:>8,} {null_pct:>6.1f}% {status:>12s}"
                )
            return "\n".join(lines)
        except Exception as e:
            return f"SQL error: {e}"

    def sql_duplicates(self, table: str, columns: list[str] | None = None) -> str:
        """Check for duplicate rows."""
        self._ensure_sql_registered()
        try:
            if columns is None:
                # Get all columns
                schema = self._sql_conn.execute(f"DESCRIBE {table}").fetchall()
                columns = [col[0] for col in schema]

            col_list = ", ".join(f'"{c}"' for c in columns)
            total = self._sql_conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            unique = self._sql_conn.execute(
                f"SELECT COUNT(DISTINCT {col_list}) FROM {table}"
            ).fetchone()[0]
            dupes = total - unique

            lines = [
                f"Duplicate check for '{table}':",
                f"  Columns checked: {', '.join(columns)}",
                f"  Total rows:      {total:,}",
                f"  Unique rows:     {unique:,}",
                f"  Duplicates:      {dupes:,} ({dupes / total * 100:.1f}%)" if total else "",
            ]

            if dupes > 0 and dupes <= 20:
                # Show sample duplicates
                result = self._sql_conn.execute(f"""
                    SELECT {col_list}, COUNT(*) AS dup_count
                    FROM {table}
                    GROUP BY {col_list}
                    HAVING COUNT(*) > 1
                    ORDER BY dup_count DESC
                    LIMIT 10
                """)
                rows = result.fetchall()
                if rows:
                    lines.append("\nSample duplicate groups:")
                    for row in rows:
                        *vals, cnt = row
                        lines.append(f"  {vals} → appears {cnt} times")
            return "\n".join(lines)
        except Exception as e:
            return f"SQL error: {e}"

    # ------------------------------------------------------------------
    # SQL – Data transformation
    # ------------------------------------------------------------------

    def sql_create_view(self, name: str, query: str) -> str:
        """Create a persistent view from a SELECT query."""
        self._ensure_sql_registered()
        try:
            self._sql_conn.execute(f"CREATE OR REPLACE VIEW {name} AS {query}")
            self._sql_views.add(name)

            # Get row count of the view
            count = self._sql_conn.execute(
                f"SELECT COUNT(*) FROM {name}"
            ).fetchone()[0]

            # Get column info
            schema = self._sql_conn.execute(f"DESCRIBE {name}").fetchall()
            cols = [f"  {c[0]:30s} {c[1]}" for c in schema]

            lines = [
                f"✅ View '{name}' created successfully.",
                f"Rows: {count:,}",
                f"\nColumns:",
            ] + cols
            return "\n".join(lines)
        except Exception as e:
            return f"CREATE VIEW error: {e}"

    def sql_export(self, query: str, path: str, format: str = "csv") -> str:
        """Export query results to a file (CSV, Parquet, JSON)."""
        self._ensure_sql_registered()
        try:
            result = self._sql_conn.execute(query)
            df = result.fetchdf()

            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)

            fmt = format.lower()
            if fmt == "csv":
                df.to_csv(p, index=False)
            elif fmt == "parquet":
                df.to_parquet(p, index=False)
            elif fmt == "json":
                df.to_json(p, orient="records", indent=2)
            else:
                return f"Unsupported format: '{format}'. Use csv, parquet, or json."

            size = p.stat().st_size
            size_str = f"{size:,} B" if size < 1024 else f"{size / 1024:.1f} KB"
            return (
                f"✅ Exported {len(df):,} rows × {len(df.columns)} columns "
                f"to {p} ({size_str}, {fmt.upper()})"
            )
        except Exception as e:
            return f"Export error: {e}"

    # ------------------------------------------------------------------
    # SQL – Comparison
    # ------------------------------------------------------------------

    def sql_compare(self, query1: str, query2: str) -> str:
        """Compare two query results and show differences."""
        self._ensure_sql_registered()
        try:
            r1 = self._sql_conn.execute(query1).fetchdf()
            r2 = self._sql_conn.execute(query2).fetchdf()

            lines = [
                f"Comparison results:",
                f"  Result 1: {len(r1):,} rows × {len(r1.columns)} cols",
                f"  Result 2: {len(r2):,} rows × {len(r2.columns)} cols",
            ]

            # Check column differences
            cols1 = set(r1.columns)
            cols2 = set(r2.columns)
            only1 = cols1 - cols2
            only2 = cols2 - cols1
            if only1:
                lines.append(f"  Columns only in result 1: {', '.join(sorted(only1))}")
            if only2:
                lines.append(f"  Columns only in result 2: {', '.join(sorted(only2))}")

            # Row counts
            diff = abs(len(r1) - len(r2))
            if diff > 0:
                bigger = "Result 1" if len(r1) > len(r2) else "Result 2"
                lines.append(f"  Row count difference: {diff:,} more rows in {bigger}")

            # If same columns and reasonable size, do set diff
            common_cols = sorted(cols1 & cols2)
            if common_cols and len(r1) < 10_000 and len(r2) < 10_000:
                # Rows in 1 but not 2
                merged = r1.merge(r2, on=common_cols, how="left", indicator=True)
                only_in_1 = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
                merged2 = r2.merge(r1, on=common_cols, how="left", indicator=True)
                only_in_2 = merged2[merged2["_merge"] == "left_only"].drop(columns=["_merge"])

                lines.append(f"\n  Rows only in result 1: {len(only_in_1):,}")
                lines.append(f"  Rows only in result 2: {len(only_in_2):,}")

                if 0 < len(only_in_1) <= 5:
                    lines.append("\n  Sample rows only in result 1:")
                    lines.append(only_in_1.head(5).to_string(index=False))
            else:
                lines.append("\n  (Skipping row-level diff — results too large or no common columns)")

            return "\n".join(lines)
        except Exception as e:
            return f"Compare error: {e}"

    # ------------------------------------------------------------------
    # SQL – Time intelligence
    # ------------------------------------------------------------------

    def sql_date_range(self, table: str, column: str) -> str:
        """Get date range and distribution for a date column."""
        self._ensure_sql_registered()
        try:
            result = self._sql_conn.execute(f"""
                SELECT
                    MIN("{column}") AS min_date,
                    MAX("{column}") AS max_date,
                    COUNT(*) AS total,
                    COUNT(DISTINCT "{column}") AS distinct_dates,
                    COUNT(*) FILTER (WHERE "{column}" IS NULL) AS nulls
                FROM {table}
            """).fetchone()

            min_d, max_d, total, distinct, nulls = result

            lines = [
                f"Date range for '{column}' in '{table}':",
                f"  Min date:       {min_d}",
                f"  Max date:       {max_d}",
                f"  Total rows:     {total:,}",
                f"  Distinct dates: {distinct:,}",
                f"  NULL values:    {nulls:,}",
            ]

            if distinct and distinct > 1 and min_d and max_d:
                # Show distribution by year/month
                try:
                    dist = self._sql_conn.execute(f"""
                        SELECT
                            DATE_TRUNC('month', "{column}"::DATE) AS month,
                            COUNT(*) AS cnt
                        FROM {table}
                        WHERE "{column}" IS NOT NULL
                        GROUP BY month
                        ORDER BY month
                    """).fetchall()

                    if dist:
                        lines.append(f"\n  Monthly distribution ({len(dist)} months):")
                        lines.append(f"  {'Month':12s} {'Count':>8s} {'Bar'}")
                        max_cnt = max(r[1] for r in dist)
                        for month, cnt in dist[:24]:  # show first 24 months
                            bar_len = int(cnt / max_cnt * 40) if max_cnt else 0
                            bar = "█" * bar_len
                            lines.append(f"  {str(month):12s} {cnt:>8,} {bar}")

                        if len(dist) > 24:
                            lines.append(f"  ... ({len(dist) - 24} more months)")
                except Exception:
                    pass  # If DATE_TRUNC fails, just skip distribution

            return "\n".join(lines)
        except Exception as e:
            return f"SQL error: {e}"

    # ------------------------------------------------------------------
    # SQL – Metadata & dependencies
    # ------------------------------------------------------------------

    def sql_dependencies(self) -> str:
        """Show potential join keys between tables."""
        self._ensure_sql_registered()
        try:
            tables = self._sql_conn.execute("SHOW TABLES").fetchall()
            if len(tables) < 2:
                return (
                    "Need at least 2 tables to analyze dependencies.\n"
                    f"Currently loaded: {len(tables)} table(s)."
                )

            lines = ["Table relationship analysis:\n"]
            table_names = [t[0] for t in tables]

            for i, t1 in enumerate(table_names):
                schema1 = self._sql_conn.execute(f"DESCRIBE {t1}").fetchall()
                cols1 = {c[0]: c[1] for c in schema1}
                lines.append(f"  📊 {t1} ({len(cols1)} columns)")

                for t2 in table_names[i + 1:]:
                    schema2 = self._sql_conn.execute(f"DESCRIBE {t2}").fetchall()
                    cols2 = {c[0]: c[1] for c in schema2}

                    # Find columns with same name (likely FK relationships)
                    same_name = set(cols1) & set(cols2)
                    # Find columns with similar names
                    similar = set()
                    for c1 in cols1:
                        for c2 in cols2:
                            if c1 != c2 and (
                                c1.lower() == c2.lower()
                                or c1.lower().replace("_", "") == c2.lower().replace("_", "")
                                or c1.lower() in c2.lower()
                                or c2.lower() in c1.lower()
                            ):
                                similar.add((c1, c2))

                    if same_name or similar:
                        lines.append(f"    ↔ {t2}:")
                        for col in sorted(same_name):
                            lines.append(f"      ✅ exact match: {col} "
                                         f"({cols1[col]} ↔ {cols2[col]})")
                        for c1, c2 in sorted(similar):
                            if c1 not in same_name and c2 not in same_name:
                                lines.append(f"      🔗 similar: {c1} ↔ {c2} "
                                             f"({cols1[c1]} ↔ {cols2[c2]})")
                    else:
                        lines.append(f"    ↔ {t2}: no obvious join keys")
                lines.append("")

            return "\n".join(lines)
        except Exception as e:
            return f"SQL error: {e}"

    def sql_size(self, table: str) -> str:
        """Get table size information."""
        self._ensure_sql_registered()
        try:
            row_count = self._sql_conn.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            col_count = len(self._sql_conn.execute(
                f"DESCRIBE {table}"
            ).fetchall())

            # Estimate memory: sample 1000 rows and extrapolate
            try:
                sample = self._sql_conn.execute(
                    f"SELECT * FROM {table} LIMIT 1000"
                ).fetchdf()
                sample_mb = sample.memory_usage(deep=True).sum() / (1024 * 1024)
                est_total_mb = sample_mb * (row_count / min(row_count, 1000))
            except Exception:
                est_total_mb = None

            lines = [
                f"Table size for '{table}':",
                f"  Rows:    {row_count:,}",
                f"  Columns: {col_count}",
            ]
            if est_total_mb is not None:
                if est_total_mb < 1:
                    lines.append(f"  Est. memory: {est_total_mb * 1024:.1f} KB")
                elif est_total_mb < 1024:
                    lines.append(f"  Est. memory: {est_total_mb:.1f} MB")
                else:
                    lines.append(f"  Est. memory: {est_total_mb / 1024:.1f} GB")

            # Show column types summary
            schema = self._sql_conn.execute(f"DESCRIBE {table}").fetchall()
            type_counts: dict[str, int] = {}
            for _, col_type, *_ in schema:
                base = col_type.upper().split("(")[0]
                type_counts[base] = type_counts.get(base, 0) + 1

            lines.append(f"\n  Column types:")
            for dtype, cnt in sorted(type_counts.items(), key=lambda x: -x[1]):
                lines.append(f"    {dtype}: {cnt}")

            return "\n".join(lines)
        except Exception as e:
            return f"SQL error: {e}"

    # ------------------------------------------------------------------
    # SQL – History
    # ------------------------------------------------------------------

    def sql_history(self, limit: int = 20) -> str:
        """Show recent query history."""
        if not self._sql_history:
            return "No SQL queries executed yet."

        lines = [f"Recent SQL queries (last {min(limit, len(self._sql_history))}):\n"]
        for i, entry in enumerate(
            self._sql_history[-limit:], start=len(self._sql_history) - min(limit, len(self._sql_history)) + 1
        ):
            status = "✅" if entry.get("success") else "❌"
            query_preview = entry["query"].strip()[:80]
            if len(entry["query"].strip()) > 80:
                query_preview += "..."
            lines.append(f"  {i:3d}. {status} {query_preview}")
        return "\n".join(lines)

    def _record_query(self, query: str, success: bool) -> None:
        """Record a query execution in history (internal)."""
        from datetime import datetime, timezone
        self._sql_history.append({
            "query": query,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        # Keep only last 500 entries
        if len(self._sql_history) > 500:
            self._sql_history = self._sql_history[-500:]

    # ------------------------------------------------------------------
    # SQL – Pivot
    # ------------------------------------------------------------------

    def sql_pivot(
        self, table: str, index: str, columns: str, values: str, agg: str = "SUM"
    ) -> str:
        """Create a pivot table."""
        self._ensure_sql_registered()
        try:
            agg_upper = agg.upper()
            valid_aggs = {"SUM", "COUNT", "AVG", "MIN", "MAX", "MEDIAN", "FIRST", "LAST"}
            if agg_upper not in valid_aggs:
                return f"Invalid aggregation '{agg}'. Use one of: {', '.join(sorted(valid_aggs))}"

            result = self._sql_conn.execute(f"""
                PIVOT {table}
                ON "{columns}"
                USING {agg_upper}("{values}")
                GROUP BY "{index}"
            """)
            return self._format_sql_result(result, max_rows=50)
        except Exception as e:
            return f"PIVOT error: {e}"

    # ------------------------------------------------------------------
    # SQL – Outlier detection
    # ------------------------------------------------------------------

    def sql_outliers(
        self, table: str, column: str, method: str = "iqr", threshold: float = 1.5
    ) -> str:
        """Detect outliers in a numeric column."""
        self._ensure_sql_registered()
        try:
            if method.lower() == "iqr":
                q1, q3 = self._sql_conn.execute(f"""
                    SELECT
                        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "{column}"),
                        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "{column}")
                    FROM {table}
                    WHERE "{column}" IS NOT NULL
                """).fetchone()
                iqr_val = q3 - q1
                lower = q1 - threshold * iqr_val
                upper = q3 + threshold * iqr_val

                total = self._sql_conn.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE \"{column}\" IS NOT NULL"
                ).fetchone()[0]

                outliers = self._sql_conn.execute(f"""
                    SELECT *
                    FROM {table}
                    WHERE "{column}" IS NOT NULL
                      AND ("{column}" < {lower} OR "{column}" > {upper})
                    ORDER BY "{column}"
                """).fetchall()

                lines = [
                    f"Outlier detection for '{column}' in '{table}' (IQR method, threshold={threshold}):",
                    f"  Q1 (25%): {q1}",
                    f"  Q3 (75%): {q3}",
                    f"  IQR:      {iqr_val}",
                    f"  Lower bound: {lower}",
                    f"  Upper bound: {upper}",
                    f"  Outliers found: {len(outliers)} / {total:,} "
                    f"({len(outliers) / total * 100:.2f}%)" if total else "",
                ]

                if outliers and len(outliers) <= 20:
                    col_names = [desc[0] for desc in self._sql_conn.execute(
                        f"DESCRIBE {table}"
                    ).fetchall()]
                    col_idx = col_names.index(column)
                    lines.append(f"\n  Outlier rows (showing {column} value):")
                    for row in outliers[:10]:
                        lines.append(f"    {column} = {row[col_idx]}")

            elif method.lower() == "zscore":
                mean, std = self._sql_conn.execute(f"""
                    SELECT AVG("{column}"), STDDEV("{column}")
                    FROM {table}
                    WHERE "{column}" IS NOT NULL
                """).fetchone()

                if std == 0:
                    return f"No variation in '{column}' — all values are identical (mean={mean})."

                total = self._sql_conn.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE \"{column}\" IS NOT NULL"
                ).fetchone()[0]

                outliers = self._sql_conn.execute(f"""
                    SELECT *
                    FROM {table}
                    WHERE "{column}" IS NOT NULL
                      AND ABS(("{column}" - {mean}) / {std}) > {threshold}
                    ORDER BY "{column}"
                """).fetchall()

                lines = [
                    f"Outlier detection for '{column}' in '{table}' (Z-score method, threshold={threshold}):",
                    f"  Mean:   {mean:.4f}",
                    f"  StdDev: {std:.4f}",
                    f"  Outliers found: {len(outliers)} / {total:,} "
                    f"({len(outliers) / total * 100:.2f}%)" if total else "",
                ]

                if outliers and len(outliers) <= 20:
                    col_names = [desc[0] for desc in self._sql_conn.execute(
                        f"DESCRIBE {table}"
                    ).fetchall()]
                    col_idx = col_names.index(column)
                    lines.append(f"\n  Outlier rows (showing {column} value):")
                    for row in outliers[:10]:
                        lines.append(f"    {column} = {row[col_idx]}")
            else:
                return f"Unknown method '{method}'. Use 'iqr' or 'zscore'."

            return "\n".join(lines)
        except Exception as e:
            return f"Outlier detection error: {e}"

    # ------------------------------------------------------------------
    # SQL – Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_sql_result(result: Any, max_rows: int = 50) -> str:
        """Format a DuckDB query result as a text table."""
        import io

        rows = result.fetchmany(max_rows)
        if not rows:
            return "Query returned no results."

        col_names = [desc[0] for desc in result.description]
        buf = io.StringIO()

        col_widths = [len(name) for name in col_names]
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(val)))

        header = " | ".join(
            name.ljust(col_widths[i]) for i, name in enumerate(col_names)
        )
        sep = "-+-".join("-" * w for w in col_widths)
        buf.write(header + "\n")
        buf.write(sep + "\n")

        for row in rows:
            buf.write(
                " | ".join(
                    str(val).ljust(col_widths[i]) for i, val in enumerate(row)
                )
                + "\n"
            )

        remaining = result.fetchone()
        if remaining is not None:
            buf.write(f"\n(Showing first {max_rows} rows — more results available)")

        return buf.getvalue()


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
