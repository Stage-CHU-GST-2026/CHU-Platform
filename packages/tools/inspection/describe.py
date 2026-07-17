"""Dataset description tools — bridge between LLM and AnalysisEngine."""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PathSchema(BaseModel):
    path: str = Field(
        description="Path to the dataset file (CSV, Excel, Parquet, etc.)")


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
            lines.append(
                f"{col:30s} {str(df[col].dtype):12s}  {nulls:>6}  {uniq:>6}")
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
# Dataset discovery
# ---------------------------------------------------------------------------


class _NoArgs(BaseModel):
    """Placeholder schema — no arguments needed."""
    pass


class ListDatasetsTool(BaseTool):
    name: str = "list_datasets"
    description: str = (
        "List all available dataset files in the project's data/ folder. "
        "Use this first when the user hasn't told you which dataset to use. "
        "Returns file names, sizes, and last modified dates."
    )
    args_schema: type[BaseModel] = _NoArgs

    def _run(self, **kwargs: str) -> str:
        from analysis.engine import _list_datasets, _find_data_dir

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
            lines.append(f"  📄 {ds.name}  ({size_str})")
        lines.append("\nUse a dataset by referencing its path, e.g.:")
        lines.append(f"  `data/{datasets[0].name}`")
        return "\n".join(lines)
