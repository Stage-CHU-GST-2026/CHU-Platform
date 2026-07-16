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


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CHART_TYPE = Literal[
    # ── basic ────────────────────────────────────────────────────────────
    "bar",          # single category → single value (x=category, y=value)
    "line",         # trend over a continuous x (x=x-axis, y=value)
    "histogram",    # distribution of one numeric column (x or y = column)
    "scatter",      # two numeric columns vs each other (x, y)
    "pie",          # part-to-whole proportions (x=label, y=value)
    "box",          # spread/quartiles for numeric columns (y = col or list)
    # ── distribution ────────────────────────────────────────────────────
    "area",         # filled area under line(s); good for cumulative views
    "kde",          # smooth density curve for one numeric column
    "violin",       # distribution shape + summary; optionally grouped by hue
    # ── comparison ──────────────────────────────────────────────────────
    "stacked_bar",  # x=category, y=value, hue=sub-group → stacked bars
    "grouped_bar",  # x=category, y=value, hue=sub-group → side-by-side bars
    "count_bar",    # frequency count of a categorical column (x=column)
    # ── relational ──────────────────────────────────────────────────────
    "bubble",       # scatter with size driven by size_col
    "pair_plot",    # pairwise scatter matrix for multiple numeric columns
    # ── sequence / flow ─────────────────────────────────────────────────
    "funnel",       # descending horizontal bars (x=label, y=value)
    "waterfall",    # running-total bars showing positive/negative deltas
    # ── correlation ─────────────────────────────────────────────────────
    "heatmap",      # 2-D color grid of numeric DataFrame values
    # ── multi-series ────────────────────────────────────────────────────
    "multi_line",   # multiple lines on one axes (x=x-axis, y=list of cols)
]

_DESCRIPTION = (
    "Generate a publication-quality chart from a dataset and return its URL. "
    "Choose the chart type that best matches the user's analytical intent:\n"
    "  bar/grouped_bar/stacked_bar → compare categories\n"
    "  line/multi_line/area        → show trends or time series\n"
    "  histogram/kde               → explore a numeric distribution\n"
    "  scatter/bubble              → reveal correlations between two (or three) numeric columns\n"
    "  pie/funnel                  → show proportions or conversion stages\n"
    "  box/violin                  → compare distributions across groups\n"
    "  heatmap                     → visualize a correlation matrix or 2-D numeric table\n"
    "  waterfall                   → show cumulative effect of sequential positive/negative values\n"
    "  count_bar                   → rank-order the frequency of a categorical column\n"
    "  pair_plot                   → pairwise relationships across many numeric columns\n"
    "Returns the URL of the generated chart image."
)


class GenerateChartSchema(BaseModel):
    path: str = Field(description="Path to the dataset file (CSV, Excel, Parquet, JSON, …).")
    chart_type: _CHART_TYPE = Field(  # type: ignore[valid-type]
        description="Type of chart. See tool description for selection guidance."
    )
    x: str | None = Field(
        default=None,
        description="Column for the x-axis / category labels / funnel labels.",
    )
    y: str | list[str] | None = Field(
        default=None,
        description=(
            "Column(s) for the y-axis / values. "
            "Pass a list for multi_line, area, box, or pair_plot."
        ),
    )
    hue: str | None = Field(
        default=None,
        description=(
            "Grouping column for violin, grouped_bar, stacked_bar, and pair_plot. "
            "Splits the data into coloured sub-groups."
        ),
    )
    size_col: str | None = Field(
        default=None,
        description="Numeric column that controls bubble size (bubble chart only).",
    )
    title: str = Field(default="", description="Chart title. Auto-generated if omitted.")
    bins: int | None = Field(
        default=None,
        description="Number of bins for histogram or kde. Defaults to auto.",
    )


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------


class GenerateChartTool(BaseTool):
    name: str = "generate_chart"
    description: str = _DESCRIPTION
    args_schema: type[BaseModel] = GenerateChartSchema

    def _run(
        self,
        path: str,
        chart_type: str = "bar",
        x: str | None = None,
        y: str | list[str] | None = None,
        hue: str | None = None,
        size_col: str | None = None,
        title: str = "",
        bins: int | None = None,
    ) -> str:
        df = _engine.load(path)

        spec = ChartSpec(
            chart_type=chart_type,  # type: ignore[arg-type]
            data=df,
            x=x,
            y=y,
            hue=hue,
            size_col=size_col,
            title=title or f"{chart_type.replace('_', ' ').title()} Chart",
            xlabel=x or "",
            ylabel=(y if isinstance(y, str) else (y[0] if y else "")),
            output_dir=_get_output_dir(),
            bins=bins,
        )
        filepath = render_chart(spec)
        filename = os.path.basename(filepath)
        api_url = f"/api/v1/charts/{filename}"
        # The CHART_URL: prefix is detected by AgentService.stream() which
        # emits a dedicated 'image' SSE event so the UI can render it inline.
        return f"{CHART_URL_PREFIX}{api_url}\nChart saved to {filepath}"
