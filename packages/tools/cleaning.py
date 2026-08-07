"""Data cleaning tools — bridge between LLM and AnalysisEngine cleaning."""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()


class PathSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")


class DropColumnsSchema(PathSchema):
    columns: list[str] = Field(description="List of column names to drop.")


class MissingValuesTool(BaseTool):
    name: str = "missing_values"
    description: str = (
        "Show missing value counts and percentages for every column in the dataset."
    )
    args_schema: type[BaseModel] = PathSchema

    def _run(self, path: str) -> str:
        df = _engine.load(path)
        summary = _engine.missing_summary(df)
        return summary.to_string()


class DuplicatesTool(BaseTool):
    name: str = "duplicates"
    description: str = "Count and show duplicate rows in the dataset."
    args_schema: type[BaseModel] = PathSchema

    def _run(self, path: str) -> str:
        df = _engine.load(path)
        dups = df.duplicated()
        count = int(dups.sum())
        if count == 0:
            return "No duplicate rows found."
        return f"Found {count} duplicate rows:\n{df[dups].head(10).to_string()}"


class DropColumnsTool(BaseTool):
    name: str = "drop_columns"
    description: str = "Drop specified columns from the dataset."
    args_schema: type[BaseModel] = DropColumnsSchema

    def _run(self, path: str, columns: list[str]) -> str:
        df = _engine.load(path)
        df2 = _engine.drop_columns(df, columns)
        remaining = ", ".join(df2.columns)
        return f"Dropped {columns}. Remaining columns ({len(df2.columns)}): {remaining}"
