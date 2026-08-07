"""Analytics tools — statistical computation, aggregations, relationships, and filtering."""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ColumnSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    column: str = Field(description="Column name.")


class QuantileSchema(ColumnSchema):
    probs: list[float] | None = Field(
        default=None,
        description="List of probabilities, e.g. [0.25, 0.5, 0.75]",
    )


class ComputeStatsSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    columns: list[str] | None = Field(
        default=None,
        description="Optional list of column names to compute statistics for. If omitted, computes statistics for all numeric columns.",
    )
    metrics: list[str] | None = Field(
        default=None,
        description="Optional list of metrics to compute (e.g. ['mean', 'median', 'std', 'min', 'max', 'count', '25%', '75%']). If omitted, computes complete statistical summary.",
    )


class AggregateSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    group_by: str = Field(description="Column name to group by.")
    agg: str = Field(
        description="Aggregation function, e.g. 'sum', 'mean', 'count', 'min', 'max'"
    )
    value_column: str = Field(description="Column to aggregate.")


class FilterSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    query: str = Field(
        description="Pandas query expression, e.g. 'age > 30' or 'city == \"Paris\"'"
    )


class SortSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    by: str = Field(description="Column to sort by.")
    ascending: bool = Field(default=False, description="Sort ascending?")


class CorrelationSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    columns: str | None = Field(
        default=None,
        description="Comma-separated column names to correlate, e.g. 'age,income,score'. If empty, uses all numeric columns.",
    )


class OutlierSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    column: str = Field(description="Column name to check for outliers.")
    factor: float = Field(default=1.5, description="IQR multiplier (default 1.5).")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class ComputeStatsTool(BaseTool):
    name: str = "compute_statistics"
    description: str = (
        "Compute comprehensive statistical metrics (count, mean, std, min, median, max, quantiles) "
        "for one or multiple columns in a single call. Use this tool instead of invoking multiple individual stat tools."
    )
    args_schema: type[BaseModel] = ComputeStatsSchema

    def _run(
        self,
        path: str,
        columns: list[str] | None = None,
        metrics: list[str] | None = None,
    ) -> str:
        df = _engine.load(path)

        if columns:
            invalid_cols = [c for c in columns if c not in df.columns]
            if invalid_cols:
                return f"Error: Column(s) {invalid_cols} not found in dataset. Available columns: {list(df.columns)}"
            target_df = df[columns]
        else:
            target_df = df.select_dtypes(include="number")
            if target_df.empty:
                return "No numeric columns found in dataset to compute statistics."

        desc = target_df.describe().T

        if metrics:
            metric_map = {m.lower(): m for m in desc.columns}
            matched_cols = []
            for m in metrics:
                mlower = m.lower()
                if mlower in metric_map:
                    matched_cols.append(metric_map[mlower])
                elif mlower in ["50%", "p50", "median"]:
                    matched_cols.append("50%")
                elif mlower in ["25%", "p25"]:
                    matched_cols.append("25%")
                elif mlower in ["75%", "p75"]:
                    matched_cols.append("75%")
            if matched_cols:
                desc = desc[matched_cols]

        lines = ["### Statistical Metrics Summary:"]
        lines.append(desc.to_string())
        return "\n".join(lines)


class MeanTool(BaseTool):
    name: str = "mean"
    description: str = "Compute the mean (average) of a numeric column."
    args_schema: type[BaseModel] = ColumnSchema

    def _run(self, path: str, column: str) -> str:
        df = _engine.load(path)
        val = df[column].mean()
        return f"Mean of '{column}': {val:.4f}"


class MedianTool(BaseTool):
    name: str = "median"
    description: str = "Compute the median of a numeric column."
    args_schema: type[BaseModel] = ColumnSchema

    def _run(self, path: str, column: str) -> str:
        df = _engine.load(path)
        val = df[column].median()
        return f"Median of '{column}': {val:.4f}"


class MinTool(BaseTool):
    name: str = "min"
    description: str = "Find the minimum value in a column."
    args_schema: type[BaseModel] = ColumnSchema

    def _run(self, path: str, column: str) -> str:
        df = _engine.load(path)
        return f"Min of '{column}': {df[column].min()}"


class MaxTool(BaseTool):
    name: str = "max"
    description: str = "Find the maximum value in a column."
    args_schema: type[BaseModel] = ColumnSchema

    def _run(self, path: str, column: str) -> str:
        df = _engine.load(path)
        return f"Max of '{column}': {df[column].max()}"


class StdTool(BaseTool):
    name: str = "std"
    description: str = "Compute the standard deviation of a numeric column."
    args_schema: type[BaseModel] = ColumnSchema

    def _run(self, path: str, column: str) -> str:
        df = _engine.load(path)
        return f"Std of '{column}': {df[column].std():.4f}"


class QuantilesTool(BaseTool):
    name: str = "quantiles"
    description: str = "Compute quantiles/percentiles of a numeric column."
    args_schema: type[BaseModel] = QuantileSchema

    def _run(self, path: str, column: str, probs: list[float] | None = None) -> str:
        df = _engine.load(path)
        result = _engine.quantiles(df, column, probs)
        lines = [f"Quantiles for '{column}':"]
        for label, val in result.items():
            lines.append(f"  {label:>5} : {val:.4f}")
        return "\n".join(lines)


class AggregateTool(BaseTool):
    name: str = "aggregate"
    description: str = (
        "Group a dataset by a column and apply an aggregation "
        "(sum, mean, count, min, max) to a value column."
    )
    args_schema: type[BaseModel] = AggregateSchema

    def _run(self, path: str, group_by: str, agg: str, value_column: str) -> str:
        df = _engine.load(path)
        result = _engine.aggregate(df, group_by=group_by, agg={value_column: agg})
        return result.to_string()


class FilterTool(BaseTool):
    name: str = "filter"
    description: str = "Filter rows using a pandas query expression."
    args_schema: type[BaseModel] = FilterSchema

    def _run(self, path: str, query: str) -> str:
        df = _engine.load(path)
        result = _engine.filter_rows(df, query)
        return result.to_string()


class SortTool(BaseTool):
    name: str = "sort"
    description: str = "Sort a dataset by a column."
    args_schema: type[BaseModel] = SortSchema

    def _run(self, path: str, by: str, ascending: bool = False) -> str:
        df = _engine.load(path)
        result = df.sort_values(by, ascending=ascending)
        return result.to_string()


class CorrelationTool(BaseTool):
    name: str = "correlation"
    description: str = "Calculate Pearson correlation between numeric columns."
    args_schema: type[BaseModel] = CorrelationSchema

    def _run(self, path: str, columns: str | None = None) -> str:
        parsed: list[str] | None = (
            [c.strip() for c in columns.split(",") if c.strip()] if columns else None
        )
        df = _engine.load(path)
        result = _engine.correlation(df, parsed)
        return result.to_string()


class OutlierDetectionTool(BaseTool):
    name: str = "outliers"
    description: str = (
        "Detect outliers in a numeric column using the IQR method. "
        "Returns the rows that are outside the IQR range."
    )
    args_schema: type[BaseModel] = OutlierSchema

    def _run(self, path: str, column: str, factor: float = 1.5) -> str:
        df = _engine.load(path)
        outliers = _engine.detect_outliers_iqr(df, column, factor=factor)
        if len(outliers) == 0:
            return f"No outliers detected in '{column}' (factor={factor})."
        return (
            f"Found {len(outliers)} outliers in '{column}' (factor={factor}):\n"
            f"{outliers.head(20).to_string()}"
        )
