"""Chart generation — produces base64-encoded PNG charts.

No AI dependencies. Uses matplotlib under the hood.
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass, field
from typing import Literal

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


@dataclass
class ChartSpec:
    """Specification for a chart."""

    chart_type: Literal["bar", "line", "histogram",
                        "scatter", "pie", "heatmap", "box"]
    data: pd.DataFrame
    x: str | None = None
    y: str | list[str] | None = None
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    figsize: tuple[int, int] = (10, 6)

    # Extra kwargs passed to the plotting method
    kwargs: dict = field(default_factory=lambda: {"color": "#2563eb"})


def render_chart(spec: ChartSpec) -> str:
    """Render a chart and return it as a base64 data URI.

    Args:
        spec: Chart specification.

    Returns:
        Base64-encoded PNG data URI.
    """
    fig, ax = plt.subplots(figsize=spec.figsize)

    try:
        _draw(ax, spec)
        ax.set_title(spec.title or spec.chart_type.title())
        if spec.xlabel:
            ax.set_xlabel(spec.xlabel)
        if spec.ylabel:
            ax.set_ylabel(spec.ylabel)
        fig.tight_layout()
    finally:
        plt.close(fig)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{b64}"


def _draw(ax: plt.Axes, spec: ChartSpec) -> None:
    """Dispatch to the correct plotting function."""
    df = spec.data
    kw = dict(spec.kwargs)

    if spec.chart_type == "bar":
        df.plot.bar(x=spec.x, y=spec.y, ax=ax, **kw)
    elif spec.chart_type == "line":
        df.plot.line(x=spec.x, y=spec.y, ax=ax, **kw)
    elif spec.chart_type == "histogram":
        col = spec.y or spec.x
        df[col].plot.hist(ax=ax, **kw)  # type: ignore[arg-type]
    elif spec.chart_type == "scatter":
        df.plot.scatter(x=spec.x, y=spec.y, ax=ax, **
                        kw)  # type: ignore[arg-type]
    elif spec.chart_type == "pie":
        df.set_index(spec.x)[spec.y].plot.pie(
            ax=ax, **kw)  # type: ignore[arg-type, index]
    elif spec.chart_type == "box":
        df[spec.y or spec.x].plot.box(ax=ax, **kw)  # type: ignore[arg-type]
    elif spec.chart_type == "heatmap":
        ax.imshow(df.values, cmap=kw.get("cmap", "viridis"), aspect="auto")
        ax.set_xticks(range(len(df.columns)))
        ax.set_xticklabels(df.columns, rotation=45, ha="right")
        ax.set_yticks(range(len(df.index)))
        ax.set_yticklabels(df.index)
        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                ax.text(j, i, f"{df.values[i, j]:.2f}",
                        ha="center", va="center", fontsize=8)

    # Remove palette from kwargs if present to avoid passing to non-color methods
    kw.pop("color", None)
    kw.pop("cmap", None)
