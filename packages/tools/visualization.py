"""Visualization tools — bridge between LLM and AnalysisEngine charts."""

from __future__ import annotations

import json
from typing import Literal

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.charts import ChartArtifact, ChartSpec, render_chart_artifact
from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()

CHARTS_DIR = "/tmp/chu_charts"

CHART_ARTIFACT_PREFIX = "CHART_ARTIFACT:"
CHART_URL_PREFIX = "CHART_URL:"


def _get_output_dir() -> str:
    import os

    os.makedirs(CHARTS_DIR, exist_ok=True)
    return CHARTS_DIR


_CHART_TYPE = Literal[
    "bar",
    "line",
    "histogram",
    "scatter",
    "pie",
    "box",
    "area",
    "kde",
    "violin",
    "stacked_bar",
    "grouped_bar",
    "count_bar",
    "bubble",
    "pair_plot",
    "funnel",
    "waterfall",
    "heatmap",
    "multi_line",
]

_DESCRIPTION = """\
Generate a chart from a dataset file and return a ChartArtifact.

## CHART LIFECYCLE — follow this protocol every time

1. COMPUTE FIRST — run the relevant statistics or aggregation before calling this tool.
2. DECIDE — only call this tool if a chart conveys information the numbers alone cannot.
3. INSIGHT FIRST — write your insight in the `insight` field BEFORE calling the tool.
   Example: "Electronics leads at $1.82M (36%), nearly double the lowest category."
4. GENERATE — call this tool with the insight.
5. REFERENCE — in your narrative, refer to the chart by its title in context.

Never generate a chart without first computing the underlying statistics.
Never generate a chart without providing a meaningful insight.
Never generate multiple charts at once for the same variable.

## CHOOSING THE RIGHT CHART TYPE

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

## REQUIRED COLUMNS PER CHART TYPE

bar, line, scatter, area, bubble, funnel, waterfall  → x AND y
histogram, kde                                        → x or y (one numeric col)
pie                                                   → x (label col) AND y (value col)
box, violin                                           → y (one or more numeric cols); hue optional
stacked_bar, grouped_bar                              → x, y, AND hue
count_bar                                             → x (categorical col, no y needed)
multi_line                                            → x AND y (list of numeric cols)
pair_plot                                             → y (list of numeric cols); hue optional
heatmap                                               → no x/y — uses all numeric columns

Returns a JSON ChartArtifact payload (title, insight, api_url, columns, …).
"""


class GenerateChartSchema(BaseModel):
    path: str = Field(
        description="Path to the dataset file (CSV, Excel, Parquet, JSON, …)."
    )
    chart_type: str = Field(
        description=(
            "Type of chart. Options: bar, line, histogram, scatter, pie, box, "
            "area, kde, violin, stacked_bar, grouped_bar, count_bar, bubble, "
            "pair_plot, funnel, waterfall, heatmap, multi_line."
        )
    )
    x: str | None = Field(
        default=None,
        description="Column for the x-axis / category labels / funnel labels.",
    )
    y: str | None = Field(
        default=None,
        description=(
            "Column name for the y-axis / values. For multi-column charts "
            "(multi_line, area, box, pair_plot), use y_columns instead."
        ),
    )
    y_columns: list[str] | None = Field(
        default=None,
        description=(
            "List of column names for multi-column chart types: multi_line, area, "
            "box, or pair_plot. Use this instead of y for multiple columns."
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
    title: str = Field(
        default="", description="Chart title. Auto-generated if omitted."
    )
    bins: int | None = Field(
        default=None,
        description="Number of bins for histogram or kde. Defaults to auto.",
    )
    insight: str = Field(
        description=(
            "REQUIRED. A 1-2 sentence interpretation of what this chart shows, "
            "written AFTER you have computed the underlying statistics."
        )
    )
    description: str = Field(
        default="",
        description="Optional. Describe what analytical question this chart answers.",
    )
    step_id: int = Field(
        default=0,
        description="Plan step index that is requesting this chart.",
    )


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
        insight: str = "",
        description: str = "",
        step_id: int = 0,
    ) -> str:
        df = _engine.load(path)
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
            ylabel=(
                y if isinstance(y, str) else (y_columns[0] if y_columns else "")
            ),
            output_dir=_get_output_dir(),
            bins=bins,
        )
        artifact = render_chart_artifact(
            spec,
            insight=insight or "No insight provided.",
            description=description,
            step_id=step_id,
        )
        return f"{CHART_ARTIFACT_PREFIX}{json.dumps(artifact.to_dict())}"


class CorrelationHeatmapSchema(BaseModel):
    path: str = Field(
        description="Path to the dataset file (CSV, Excel, Parquet, JSON, …)."
    )
    columns: str | None = Field(
        default=None,
        description="Optional comma-separated list of numeric column names to include.",
    )
    title: str = Field(
        default="Correlation Heatmap",
        description="Chart title.",
    )
    insight: str = Field(
        description="REQUIRED. A 1-2 sentence interpretation of the correlation pattern."
    )
    description: str = Field(
        default="",
        description="Optional. Describe what question this heatmap answers.",
    )
    step_id: int = Field(
        default=0,
        description="Plan step index that is requesting this chart.",
    )


class CorrelationHeatmapTool(BaseTool):
    name: str = "correlation_heatmap"
    description: str = (
        "Compute the Pearson correlation matrix for a dataset and render it as an annotated heatmap image."
    )
    args_schema: type[BaseModel] = CorrelationHeatmapSchema

    def _run(
        self,
        path: str,
        columns: str | None = None,
        title: str = "Correlation Heatmap",
        insight: str = "",
        description: str = "",
        step_id: int = 0,
    ) -> str:
        df = _engine.load(path)
        cols: list[str] | None = (
            [c.strip() for c in columns.split(",") if c.strip()] if columns else None
        )
        corr_df = _engine.correlation(df, cols)

        spec = ChartSpec(
            chart_type="heatmap",
            data=corr_df,
            title=title,
            output_dir=_get_output_dir(),
        )
        artifact = render_chart_artifact(
            spec,
            insight=insight or "Correlation matrix computed.",
            description=description
            or "Pearson correlation matrix of numeric columns.",
            step_id=step_id,
        )
        return f"{CHART_ARTIFACT_PREFIX}{json.dumps(artifact.to_dict())}"
