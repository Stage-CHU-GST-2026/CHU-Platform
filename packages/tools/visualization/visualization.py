"""Visualization tools — bridge between LLM and AnalysisEngine charts."""

from __future__ import annotations

import os
from typing import Literal

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.charts import ChartSpec, render_chart
from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()

# Output directory: CHU-Platform/outputs/charts/
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJ_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
_OUTPUT_DIR = os.path.join(_PROJ_ROOT, "outputs", "charts")


def _get_output_dir() -> str:
    os.makedirs(_OUTPUT_DIR, exist_ok=True)
    return _OUTPUT_DIR


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
        return f"Chart saved: {filepath}"
