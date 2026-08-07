"""Dataset inspection tools — bridge between LLM and AnalysisEngine."""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class PathSchema(BaseModel):
    path: str = Field(description="Path to the dataset file (CSV, Excel, Parquet, etc.)")


class HeadSchema(PathSchema):
    n: int = Field(default=5, description="Number of rows to preview (max 20)")


class ColumnSchema(PathSchema):
    column: str = Field(description="Name of the column to analyze")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class DescribeDatasetTool(BaseTool):
    name: str = "describe_dataset"
    description: str = (
        "Load a dataset and return its shape, column names, dtypes, "
        "null counts, unique counts, and a sample value per column."
    )
    args_schema: type[BaseModel] = PathSchema

    def _run(self, path: str) -> str:
        df = _engine.load(path)
        return _engine.profile(df).formatted()


class DatasetSummaryTool(BaseTool):
    name: str = "dataset_summary"
    description: str = (
        "Statistical summary of numeric columns (like pandas describe). "
        "Use this to understand distributions, means, std devs, etc."
    )
    args_schema: type[BaseModel] = PathSchema

    def _run(self, path: str) -> str:
        df = _engine.load(path)
        return _engine.describe(df, include_all=True)


class DatasetHeadTool(BaseTool):
    name: str = "dataset_head"
    description: str = "Preview the first N rows of a dataset."
    args_schema: type[BaseModel] = HeadSchema

    def _run(self, path: str, n: int = 5) -> str:
        df = _engine.load(path)
        return _engine.head(df, n=n).to_string()


class DatasetShapeTool(BaseTool):
    name: str = "dataset_shape"
    description: str = "Return the shape (rows, columns) of a dataset."
    args_schema: type[BaseModel] = PathSchema

    def _run(self, path: str) -> str:
        df = _engine.load(path)
        return f"Shape: {len(df):,} rows × {len(df.columns)} columns"


class ListColumnsTool(BaseTool):
    name: str = "list_columns"
    description: str = "List all column names and their data types in a dataset."
    args_schema: type[BaseModel] = PathSchema

    def _run(self, path: str) -> str:
        df = _engine.load(path)
        lines = [f"{'Column':30s} {'Dtype':12s}  {'Nulls':>6}  {'Unique':>6}"]
        lines.append("-" * 60)
        for col in df.columns:
            nulls = df[col].isna().sum()
            uniq = df[col].nunique()
            lines.append(f"{col:30s} {str(df[col].dtype):12s}  {nulls:>6}  {uniq:>6}")
        return "\n".join(lines)


class ColumnInfoTool(BaseTool):
    name: str = "column_info"
    description: str = (
        "Detailed statistics for a single column: min, max, mean, "
        "quantiles for numeric; top values for categorical."
    )
    args_schema: type[BaseModel] = ColumnSchema

    def _run(self, path: str, column: str) -> str:
        df = _engine.load(path)
        return _engine.column_info(df, column)


# ---------------------------------------------------------------------------
# Dataset discovery — supports both DB-backed and filesystem modes
# ---------------------------------------------------------------------------

_registered_datasets: list[dict] = []


def register_datasets(datasets: list[dict]) -> None:
    """Inject a list of datasets from the database (called by the API at startup)."""
    global _registered_datasets
    _registered_datasets = list(datasets)


def clear_registered_datasets() -> None:
    """Clear the registry (useful for testing)."""
    global _registered_datasets
    _registered_datasets = []


class _NoArgs(BaseModel):
    """Placeholder schema — no arguments needed."""

    pass


class ListDatasetsTool(BaseTool):
    name: str = "list_datasets"
    description: str = (
        "List all available datasets. "
        "Use this first when you don't know which dataset to use. "
        "Returns filenames, sizes, row/column counts, and file paths."
    )
    args_schema: type[BaseModel] = _NoArgs

    def _run(self, **kwargs: str) -> str:
        if _registered_datasets:
            ready = [d for d in _registered_datasets if d.get("status") == "ready"]
            if not ready:
                ready = _registered_datasets

            lines = [f"Found {len(ready)} dataset(s):\n"]
            for ds in ready:
                fname = ds.get("original_filename", "unknown")
                rows = ds.get("rows")
                cols = ds.get("columns")
                size_bytes = ds.get("file_size")
                status = ds.get("status", "unknown")

                if size_bytes:
                    if size_bytes < 1024:
                        size_str = f"{size_bytes} B"
                    elif size_bytes < 1024**2:
                        size_str = f"{size_bytes / 1024:.1f} KB"
                    else:
                        size_str = f"{size_bytes / 1024**2:.1f} MB"
                else:
                    size_str = "?"

                row_str = f"{rows:,}" if rows else "?"
                col_str = f"{cols}" if cols else "?"

                status_tag = (
                    "[ready]"
                    if status == "ready"
                    else "[processing]"
                    if status in ("uploading", "processing")
                    else "[error]"
                )
                lines.append(
                    f"  {status_tag} {fname}  ({row_str} rows × {col_str} cols, {size_str})"
                )

            lines.append("\nReference a dataset by its full path, e.g.:")
            first_path = ready[0].get("filepath", "")
            if first_path:
                lines.append(f"  `{first_path}`")
            return "\n".join(lines)

        from analysis.engine import _find_data_dir, _list_datasets

        data_dir = _find_data_dir()
        if data_dir is None:
            return "No data/ folder found in the project."

        datasets = _list_datasets(data_dir)
        if not datasets:
            return f"The data/ folder ({data_dir}) exists but contains no supported dataset files."

        lines = [f"Found {len(datasets)} dataset(s) in {data_dir}:\n"]
        for ds in datasets:
            size = ds.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024**2:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / 1024**2:.1f} MB"
            lines.append(f"  [file] {ds.name}  ({size_str})")
        lines.append("\nUse a dataset by referencing its path, e.g.:")
        lines.append(f"  `data/{datasets[0].name}`")
        return "\n".join(lines)
