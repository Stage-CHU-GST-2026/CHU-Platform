"""Statistical tools — bridge between LLM and AnalysisEngine statistics."""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()


class ColumnSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    column: str = Field(description="Column name.")


class QuantileSchema(ColumnSchema):
    probs: list[float] | None = Field(
        default=None,
        description="List of probabilities, e.g. [0.25, 0.5, 0.75]",
    )


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
