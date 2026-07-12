"""Visualization tools — bridge between LLM and AnalysisEngine charts."""

from __future__ import annotations

from typing import Literal

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.charts import ChartSpec, render_chart
from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()


class ChartSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    chart_type: Literal["bar", "line", "histogram", "scatter", "pie", "box"] = Field(
        description="Type of chart to generate."
    )
    x: str | None = Field(
        default=None, description="Column for the x-axis / categories.")
    y: str | None = Field(
        default=None, description="Column for the y-axis / values.")
    title: str = Field(default="", description="Chart title.")


class BarChartTool(BaseTool):
    name: str = "bar_chart"
    description: str = "Generate a bar chart from two columns and return it as an image."
    args_schema: type[BaseModel] = ChartSchema

    def _run(
        self,
        path: str,
        chart_type: str = "bar",
        x: str | None = None,
        y: str | None = None,
        title: str = "",
    ) -> str:
        df = _engine.load(path)
        spec = ChartSpec(
            chart_type="bar",
            data=df,
            x=x,
            y=y,
            title=title or f"Bar Chart: {y or ''} by {x or ''}",
            xlabel=x or "",
            ylabel=y or "",
        )
        return render_chart(spec)


class HistogramTool(BaseTool):
    name: str = "histogram"
    description: str = "Generate a histogram for a numeric column."
    args_schema: type[BaseModel] = ChartSchema

    def _run(
        self,
        path: str,
        chart_type: str = "histogram",
        x: str | None = None,
        y: str | None = None,
        title: str = "",
    ) -> str:
        df = _engine.load(path)
        col = y or x
        spec = ChartSpec(
            chart_type="histogram",
            data=df,
            x=col,
            title=title or f"Histogram of '{col}'",
            xlabel=col or "",
            ylabel="Frequency",
        )
        return render_chart(spec)


class ScatterPlotTool(BaseTool):
    name: str = "scatter_plot"
    description: str = "Generate a scatter plot of two numeric columns."
    args_schema: type[BaseModel] = ChartSchema

    def _run(
        self,
        path: str,
        chart_type: str = "scatter",
        x: str | None = None,
        y: str | None = None,
        title: str = "",
    ) -> str:
        df = _engine.load(path)
        spec = ChartSpec(
            chart_type="scatter",
            data=df,
            x=x,
            y=y,
            title=title or f"Scatter: {y or ''} vs {x or ''}",
            xlabel=x or "",
            ylabel=y or "",
        )
        return render_chart(spec)


class LineChartTool(BaseTool):
    name: str = "line_chart"
    description: str = "Generate a line chart from two columns."
    args_schema: type[BaseModel] = ChartSchema

    def _run(
        self,
        path: str,
        chart_type: str = "line",
        x: str | None = None,
        y: str | None = None,
        title: str = "",
    ) -> str:
        df = _engine.load(path)
        spec = ChartSpec(
            chart_type="line",
            data=df,
            x=x,
            y=y,
            title=title or f"Line Chart: {y or ''} over {x or ''}",
            xlabel=x or "",
            ylabel=y or "",
        )
        return render_chart(spec)
