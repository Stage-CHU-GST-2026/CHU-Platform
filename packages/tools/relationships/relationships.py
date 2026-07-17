"""Relationship/outlier tools — bridge between LLM and AnalysisEngine."""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()


class CorrelationSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    columns: str | None = Field(
        default=None,
        description="Comma-separated column names to correlate, e.g. 'age,income,score'. If empty, uses all numeric columns.",
    )


class OutlierSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    column: str = Field(description="Column name to check for outliers.")
    factor: float = Field(
        default=1.5, description="IQR multiplier (default 1.5).")


class CorrelationTool(BaseTool):
    name: str = "correlation"
    description: str = "Calculate Pearson correlation between numeric columns."
    args_schema: type[BaseModel] = CorrelationSchema

    def _run(self, path: str, columns: str | None = None) -> str:
        # Parse comma-separated string into a list
        parsed: list[str] | None = (
            [c.strip() for c in columns.split(",") if c.strip()]
            if columns else None
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
