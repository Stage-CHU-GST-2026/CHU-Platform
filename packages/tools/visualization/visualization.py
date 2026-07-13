"""Visualization tools — bridge between LLM and AnalysisEngine charts."""

from __future__ import annotations

import os
from typing import Literal

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.charts import ChartSpec, render_chart
from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()

# Fixed output directory served as static files by the API.
# The API mounts this directory at /api/v1/charts.
CHARTS_DIR = "/tmp/chu_charts"

# Prefix embedded in tool output so the streaming layer can detect chart URLs.
CHART_URL_PREFIX = "CHART_URL:"


def _get_output_dir() -> str:
    os.makedirs(CHARTS_DIR, exist_ok=True)
    return CHARTS_DIR


class GenerateChartSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    chart_type: Literal["bar", "line", "histogram", "scatter", "pie", "box"] = Field(
        description="Type of chart to generate."
    )
    x: str | None = Field(
        default=None, description="Column for the x-axis / categories."
    )
    y: str | None = Field(
        default=None, description="Column for the y-axis / values."
    )
    title: str = Field(default="", description="Chart title.")
    bins: int | None = Field(
        default=None, description="Number of bins (for histogram only)."
    )


class GenerateChartTool(BaseTool):
    name: str = "generate_chart"
    description: str = (
        "Generate a chart from dataset columns and save it as a PNG file. "
        "Supports: bar, line, histogram, scatter, pie, box. "
        "Returns the file path to the saved chart."
    )
    args_schema: type[BaseModel] = GenerateChartSchema

    def _run(
        self,
        path: str,
        chart_type: str = "bar",
        x: str | None = None,
        y: str | None = None,
        title: str = "",
        bins: int | None = None,
    ) -> str:
        df = _engine.load(path)

        kwargs = {}
        if chart_type == "histogram" and bins:
            kwargs["bins"] = bins

        spec = ChartSpec(
            chart_type=chart_type,  # type: ignore[arg-type]
            data=df,
            x=x,
            y=y,
            title=title or f"{chart_type.title()} Chart",
            xlabel=x or "",
            ylabel=y or "",
            output_dir=_get_output_dir(),
            kwargs=kwargs,
        )
        filepath = render_chart(spec)
        filename = os.path.basename(filepath)
        api_url = f"/api/v1/charts/{filename}"
        # The CHART_URL: prefix is detected by AgentService.stream() which
        # emits a dedicated 'image' SSE event so the UI can render it inline.
        return f"{CHART_URL_PREFIX}{api_url}\nChart saved to {filepath}"
