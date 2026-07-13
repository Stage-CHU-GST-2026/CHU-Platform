"""Relationship/outlier tools — bridge between LLM and AnalysisEngine."""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()


class CorrelationSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    columns: list[str] | str | None = Field(
        default=None,
        description="Columns to correlate (comma-separated string or list). If empty, uses all numeric columns.",
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

    def _run(self, path: str, columns: list[str] | str | None = None) -> str:
        # LLMs sometimes pass columns as a comma-separated string
        if isinstance(columns, str):
            columns = [c.strip() for c in columns.split(",") if c.strip()]
        df = _engine.load(path)
        result = _engine.correlation(df, columns)
        return result.to_string()


class OutlierDetectionTool(BaseTool):
    name: str = "outliers"
    description: str = (
        "Detect outliers in a numeric column using the IQR method. "
        "Returns the rows that are outside the IQR range."
    )
    args_schema: type[BaseModel] = OutlierSchema

    def _run(self, path: str, column: str, factor: float = 1.5) -> str:
        # Groq envoie parfois factor en string — on le convertit
        factor = float(factor)  # type: ignore[arg-type]
        df = _engine.load(path)
        outliers = _engine.detect_outliers_iqr(df, column, factor=factor)
        if len(outliers) == 0:
            return f"No outliers detected in '{column}' (factor={factor})."
        return (
            f"Found {len(outliers)} outliers in '{column}' (factor={factor}):\n"
            f"{outliers.head(20).to_string()}"
        )
