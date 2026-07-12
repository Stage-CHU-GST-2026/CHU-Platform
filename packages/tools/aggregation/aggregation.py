"""Aggregation tools — bridge between LLM and AnalysisEngine aggregation."""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()


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


class AggregateTool(BaseTool):
    name: str = "aggregate"
    description: str = (
        "Group a dataset by a column and apply an aggregation "
        "(sum, mean, count, min, max) to a value column."
    )
    args_schema: type[BaseModel] = AggregateSchema

    def _run(self, path: str, group_by: str, agg: str, value_column: str) -> str:
        df = _engine.load(path)
        result = _engine.aggregate(
            df, group_by=group_by, agg={value_column: agg})
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
