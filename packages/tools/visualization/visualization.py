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

_DESCRIPTION = """Generate a chart from a dataset file and return its URL for display.

WHEN TO USE THIS TOOL
─────────────────────
Call this tool whenever the user asks to "plot", "visualise", "show a chart/graph/figure",
or whenever a visual summary would make data clearer than a table or plain text.
Always prefer a chart over a raw table when the user is asking about trends,
distributions, comparisons, or proportions.

CHOOSING THE RIGHT CHART TYPE
──────────────────────────────
Goal                                   → Best chart type(s)
─────────────────────────────────────────────────────────────
Compare values across categories       → bar, grouped_bar, count_bar
Compare values split by a sub-group   → grouped_bar (hue=sub-group col)
Show part-to-whole proportions        → pie, stacked_bar (hue=sub-group)
Show a trend over time / ordered x    → line, multi_line, area
Show multiple trends on one plot      → multi_line (y = list of columns)
Explore how one numeric col is spread → histogram, kde, box, violin
Compare spreads across groups         → box (y = list of cols) or violin (hue=group col)
Find correlation between two numerics → scatter
Three-variable relationship           → bubble (size_col = 3rd column)
Pairwise relationships, many cols     → pair_plot
Show a conversion / pipeline funnel   → funnel
Show running total with +/– steps     → waterfall
Visualise a correlation matrix        → heatmap (pass the correlation DataFrame)
Frequency count of a category col     → count_bar (only x is required)

REQUIRED COLUMNS PER CHART TYPE
────────────────────────────────
bar, line, scatter, area, bubble, funnel, waterfall  → x AND y
histogram, kde                                        → x or y (one numeric col)
pie                                                   → x (label col) AND y (value col)
box, violin                                           → y (one or more numeric cols); hue optional
stacked_bar, grouped_bar                              → x, y, AND hue
count_bar                                             → x (categorical col, no y needed)
multi_line                                            → x AND y (list of numeric cols)
pair_plot                                             → y (list of numeric cols); hue optional
heatmap                                               → no x/y — uses all numeric columns

WORKFLOW
────────
1. Inspect the dataset with describe_dataset or list_columns if you do not already know column names.
2. Pick the chart type from the table above.
3. Map the correct dataset columns to x, y, hue, and size_col.
4. Set a clear, descriptive title.
5. Call this tool — the returned URL is automatically rendered as an inline image.

Returns the URL of the generated PNG chart."""


class GenerateChartSchema(BaseModel):
    path: str = Field(
        description="Path to the dataset file (CSV, Excel, Parquet, JSON, …).")
    chart_type: str = Field(
        description="Type of chart. Options: bar, line, histogram, scatter, pie, box, area, kde, violin, stacked_bar, grouped_bar, count_bar, bubble, pair_plot, funnel, waterfall, heatmap, multi_line. See tool description for selection guidance."
    )
    x: str | None = Field(
        default=None,
        description="Column for the x-axis / category labels / funnel labels.",
    )
    y: str | None = Field(
        default=None,
        description="Column name for the y-axis / values. For multi-column charts (multi_line, area, box, pair_plot), use y_columns instead.",
    )
    y_columns: list[str] | None = Field(
        default=None,
        description="List of column names for multi-column chart types: multi_line, area, box, or pair_plot. Use this instead of y for multiple columns.",
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
    title: str = Field(
        default="", description="Chart title. Auto-generated if omitted.")
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
        y: str | None = None,
        y_columns: list[str] | None = None,
        hue: str | None = None,
        size_col: str | None = None,
        title: str = "",
        bins: int | None = None,
    ) -> str:
        df = _engine.load(path)

        # Use y_columns for multi-column chart types, otherwise use y
        resolved_y: str | list[str] | None = y_columns if y_columns else y

        spec = ChartSpec(
            chart_type=chart_type,  # type: ignore[arg-type]
            data=df,
            x=x,
            y=resolved_y,
            hue=hue,
            size_col=size_col,
            title=title or f"{chart_type.replace('_', ' ').title()} Chart",
            xlabel=x or "",
            ylabel=(y if isinstance(y, str) else (
                y_columns[0] if y_columns else "")),
            output_dir=_get_output_dir(),
            bins=bins,
        )
        filepath = render_chart(spec)
        filename = os.path.basename(filepath)
        api_url = f"/api/v1/charts/{filename}"
        # The CHART_URL: prefix is detected by AgentService.stream() which
        # emits a dedicated 'image' SSE event so the UI can render it inline.
        return f"{CHART_URL_PREFIX}{api_url}\nChart saved to {filepath}"


# ---------------------------------------------------------------------------
# Correlation Heatmap — dedicated tool (load + correlate + plot in one step)
# ---------------------------------------------------------------------------


class CorrelationHeatmapSchema(BaseModel):
    path: str = Field(
        description="Path to the dataset file (CSV, Excel, Parquet, JSON, …).")
    columns: str | None = Field(
        default=None,
        description=(
            "Optional comma-separated list of numeric column names to include, "
            "e.g. 'age,income,score'. If omitted, all numeric columns are used."
        ),
    )
    title: str = Field(
        default="Correlation Heatmap",
        description="Chart title.",
    )


class CorrelationHeatmapTool(BaseTool):
    name: str = "correlation_heatmap"
    description: str = (
        "Compute the Pearson correlation matrix for a dataset and render it as an "
        "annotated heatmap image. "
        "Use this tool whenever the user asks for a 'correlation heatmap', "
        "'correlation matrix', or wants to see how numeric columns relate to each other. "
        "Returns the URL of the generated heatmap — displayed inline in the chat. "
        "Do NOT write Python code; call this tool directly."
    )
    args_schema: type[BaseModel] = CorrelationHeatmapSchema

    def _run(
        self,
        path: str,
        columns: str | None = None,
        title: str = "Correlation Heatmap",
    ) -> str:
        df = _engine.load(path)

        # Select columns
        cols: list[str] | None = (
            [c.strip() for c in columns.split(",") if c.strip()]
            if columns else None
        )
        corr_df = _engine.correlation(df, cols)

        spec = ChartSpec(
            chart_type="heatmap",
            data=corr_df,
            title=title,
            output_dir=_get_output_dir(),
        )
        filepath = render_chart(spec)
        filename = os.path.basename(filepath)
        api_url = f"/api/v1/charts/{filename}"
        return f"{CHART_URL_PREFIX}{api_url}\nCorrelation heatmap saved to {filepath}"
