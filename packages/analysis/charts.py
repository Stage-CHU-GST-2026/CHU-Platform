"""Chart generation — produces PNG chart files.

No AI dependencies. Uses matplotlib (and optionally seaborn) under the hood.
Styling is left entirely to matplotlib defaults (no custom colours or themes).

Supported chart types
---------------------
Basic:        bar, line, histogram, scatter, pie, box
Distribution: area, kde, violin
Comparison:   stacked_bar, grouped_bar, count_bar
Relational:   bubble, pair_plot
Sequence:     funnel, waterfall
Correlation:  heatmap
Multi-series: multi_line
"""

from __future__ import annotations

import os
import tempfile
import uuid
import warnings
from dataclasses import dataclass, field
from typing import Literal

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")


# ---------------------------------------------------------------------------
# Chart type literal
# ---------------------------------------------------------------------------

ChartType = Literal[
    # ── basic ──────────────────────────────────────────────────────────────
    "bar",
    "line",
    "histogram",
    "scatter",
    "pie",
    "box",
    # ── distribution ───────────────────────────────────────────────────────
    "area",
    "kde",
    "violin",
    # ── comparison ─────────────────────────────────────────────────────────
    "stacked_bar",
    "grouped_bar",
    "count_bar",
    # ── relational ─────────────────────────────────────────────────────────
    "bubble",
    "pair_plot",
    # ── sequence / flow ────────────────────────────────────────────────────
    "funnel",
    "waterfall",
    # ── correlation ────────────────────────────────────────────────────────
    "heatmap",
    # ── multi-series ───────────────────────────────────────────────────────
    "multi_line",
]


# ---------------------------------------------------------------------------
# Spec dataclass
# ---------------------------------------------------------------------------


@dataclass
class ChartSpec:
    """Specification for a chart."""

    chart_type: ChartType
    data: pd.DataFrame
    x: str | None = None
    y: str | list[str] | None = None
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    figsize: tuple[int, int] = (10, 6)
    output_dir: str | None = None

    # extended parameters
    hue: str | None = None          # grouping column (violin, stacked_bar, grouped_bar)
    size_col: str | None = None     # column driving bubble size
    bins: int | None = None         # bins for histogram / kde
    kwargs: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Public render function
# ---------------------------------------------------------------------------


def render_chart(spec: ChartSpec) -> str:
    """Render a chart and save it as a PNG file.

    Args:
        spec: Chart specification.

    Returns:
        Absolute path to the saved PNG file.
    """
    if spec.chart_type == "pair_plot":
        return _render_pair_plot(spec)

    fig, ax = plt.subplots(figsize=spec.figsize)

    try:
        _draw(ax, spec)
        ax.set_title(spec.title or _default_title(spec))
        if spec.xlabel:
            ax.set_xlabel(spec.xlabel)
        if spec.ylabel:
            ax.set_ylabel(spec.ylabel)
        fig.tight_layout()
    finally:
        plt.close(fig)

    return _save(fig, spec)


# ---------------------------------------------------------------------------
# Internal: dispatch
# ---------------------------------------------------------------------------


def _draw(ax: plt.Axes, spec: ChartSpec) -> None:  # noqa: PLR0912
    """Dispatch to the correct plotting function."""
    ct = spec.chart_type
    df = spec.data

    if ct == "bar":
        _bar(ax, df, spec)
    elif ct == "line":
        _line(ax, df, spec)
    elif ct == "histogram":
        _histogram(ax, df, spec)
    elif ct == "scatter":
        _scatter(ax, df, spec)
    elif ct == "pie":
        _pie(ax, df, spec)
    elif ct == "box":
        _box(ax, df, spec)
    elif ct == "heatmap":
        _heatmap(ax, df, spec)
    elif ct == "area":
        _area(ax, df, spec)
    elif ct == "kde":
        _kde(ax, df, spec)
    elif ct == "violin":
        _violin(ax, df, spec)
    elif ct == "stacked_bar":
        _stacked_bar(ax, df, spec)
    elif ct == "grouped_bar":
        _grouped_bar(ax, df, spec)
    elif ct == "count_bar":
        _count_bar(ax, df, spec)
    elif ct == "bubble":
        _bubble(ax, df, spec)
    elif ct == "funnel":
        _funnel(ax, df, spec)
    elif ct == "waterfall":
        _waterfall(ax, df, spec)
    elif ct == "multi_line":
        _multi_line(ax, df, spec)
    else:
        raise ValueError(f"Unknown chart_type: {ct!r}")


# ---------------------------------------------------------------------------
# Chart implementations (matplotlib defaults — no forced colours)
# ---------------------------------------------------------------------------


def _bar(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "bar")
    col_y = _require(spec.y, "y", "bar")
    ax.bar(df[col_x].astype(str), df[col_y])
    ax.tick_params(axis="x", rotation=35)


def _line(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "line")
    col_y = _require(spec.y, "y", "line")
    ax.plot(df[col_x], df[col_y], marker="o", markersize=4)


def _histogram(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col = spec.y or spec.x
    col = _require(col, "x or y", "histogram")
    bins = spec.bins or "auto"
    ax.hist(df[col], bins=bins, edgecolor="white", linewidth=0.5)


def _scatter(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "scatter")
    col_y = _require(spec.y, "y", "scatter")
    ax.scatter(df[col_x], df[col_y], alpha=0.7)


def _pie(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_label = _require(spec.x, "x", "pie")
    col_val = _require(spec.y, "y", "pie")
    ax.pie(
        df[col_val],
        labels=df[col_label].astype(str),
        autopct="%1.1f%%",
        startangle=140,
    )
    ax.set_aspect("equal")


def _box(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    cols = spec.y or spec.x
    cols = [cols] if isinstance(cols, str) else list(cols)  # type: ignore[arg-type]
    data = [df[c].dropna() for c in cols]
    ax.boxplot(data, tick_labels=cols, patch_artist=True)


def _heatmap(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    numeric_df = df.select_dtypes(include="number")
    img = ax.imshow(numeric_df.values, cmap="viridis", aspect="auto")
    plt.colorbar(img, ax=ax, fraction=0.03, pad=0.02)
    ax.set_xticks(range(len(numeric_df.columns)))
    ax.set_xticklabels(numeric_df.columns, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(numeric_df.index)))
    ax.set_yticklabels(numeric_df.index, fontsize=9)
    for i in range(len(numeric_df.index)):
        for j in range(len(numeric_df.columns)):
            ax.text(
                j, i, f"{numeric_df.values[i, j]:.2f}",
                ha="center", va="center", fontsize=7.5,
            )


def _area(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "area")
    cols_y = [spec.y] if isinstance(spec.y, str) else list(spec.y or [])
    if not cols_y:
        raise ValueError("area chart requires at least one y column")
    for col in cols_y:
        ax.fill_between(df[col_x], df[col], alpha=0.5, label=col)
        ax.plot(df[col_x], df[col], linewidth=1.5)
    if len(cols_y) > 1:
        ax.legend()


def _kde(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col = spec.y or spec.x
    col = _require(col, "x or y", "kde")
    try:
        import seaborn as sns
        sns.kdeplot(data=df, x=col, ax=ax, fill=True, linewidth=2)
    except ImportError:
        from scipy.stats import gaussian_kde  # type: ignore[import]
        vals = df[col].dropna().values
        kde = gaussian_kde(vals)
        xs = np.linspace(vals.min(), vals.max(), 300)
        ax.plot(xs, kde(xs), linewidth=2)
        ax.fill_between(xs, kde(xs), alpha=0.35)


def _violin(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_y = _require(spec.y, "y", "violin")
    try:
        import seaborn as sns
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            sns.violinplot(
                data=df,
                x=spec.hue if spec.hue else None,
                y=col_y,
                hue=spec.hue if spec.hue else None,
                ax=ax,
                inner="box",
                linewidth=1.2,
                legend=False,
            )
    except ImportError:
        if spec.hue and spec.hue in df.columns:
            groups = [grp[col_y].dropna().values for _, grp in df.groupby(spec.hue)]
            labels = [str(k) for k, _ in df.groupby(spec.hue)]
        else:
            groups = [df[col_y].dropna().values]
            labels = [col_y]
        ax.violinplot(groups, showmedians=True)
        ax.set_xticks(range(1, len(labels) + 1))
        ax.set_xticklabels(labels, rotation=30)


def _stacked_bar(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "stacked_bar")
    hue_col = spec.hue or _require(None, "hue", "stacked_bar")
    val_col = _require(spec.y, "y", "stacked_bar")
    pivot = df.pivot_table(index=col_x, columns=hue_col,
                           values=val_col, aggfunc="sum", fill_value=0)
    bottom = np.zeros(len(pivot))
    for col in pivot.columns:
        ax.bar(pivot.index.astype(str), pivot[col], bottom=bottom, label=str(col))
        bottom += pivot[col].values
    ax.legend(title=hue_col)
    ax.tick_params(axis="x", rotation=35)


def _grouped_bar(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "grouped_bar")
    hue_col = spec.hue or _require(None, "hue", "grouped_bar")
    val_col = _require(spec.y, "y", "grouped_bar")
    pivot = df.pivot_table(index=col_x, columns=hue_col,
                           values=val_col, aggfunc="sum", fill_value=0)
    n_groups = len(pivot)
    n_bars = len(pivot.columns)
    width = 0.8 / n_bars
    xs = np.arange(n_groups)
    for i, col in enumerate(pivot.columns):
        offset = (i - n_bars / 2 + 0.5) * width
        ax.bar(xs + offset, pivot[col], width=width * 0.9, label=str(col))
    ax.set_xticks(xs)
    ax.set_xticklabels(pivot.index.astype(str), rotation=35)
    ax.legend(title=hue_col)


def _count_bar(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col = spec.x or spec.y
    col = _require(col, "x", "count_bar")
    counts = df[col].value_counts().sort_values(ascending=True)
    ax.barh(counts.index.astype(str), counts.values)


def _bubble(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "bubble")
    col_y = _require(spec.y, "y", "bubble")
    size_col = spec.size_col
    if size_col and size_col in df.columns:
        raw = df[size_col].fillna(0)
        sizes = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9) * 900 + 30
    else:
        sizes = 80
    ax.scatter(df[col_x], df[col_y], s=sizes, alpha=0.7)
    if size_col:
        ax.set_title((spec.title or "Bubble Chart") + f"  (size ∝ {size_col})")


def _funnel(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_label = _require(spec.x, "x", "funnel")
    col_val = _require(spec.y, "y", "funnel")
    data = df[[col_label, col_val]].sort_values(col_val, ascending=False)
    max_val = data[col_val].max()
    prop_cycle = plt.rcParams["axes.prop_cycle"]
    colours = [c["color"] for c in prop_cycle]
    for i, (_, row) in enumerate(data.iterrows()):
        width = row[col_val] / max_val
        left = (1 - width) / 2
        ax.barh(i, width, left=left, height=0.7, color=colours[i % len(colours)])
        ax.text(0.5, i, f"{row[col_label]}  ({row[col_val]:,.0f})",
                ha="center", va="center", fontsize=9.5, fontweight="bold")
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(data) - 0.5)
    ax.invert_yaxis()
    ax.grid(False)


def _waterfall(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_label = _require(spec.x, "x", "waterfall")
    col_val = _require(spec.y, "y", "waterfall")
    labels = df[col_label].astype(str).tolist()
    values = df[col_val].tolist()

    running = 0.0
    bottoms, tops, colors = [], [], []
    for v in values:
        if v >= 0:
            bottoms.append(running)
            tops.append(v)
            colors.append("steelblue")
        else:
            bottoms.append(running + v)
            tops.append(-v)
            colors.append("tomato")
        running += v

    ax.bar(labels, tops, bottom=bottoms, color=colors, width=0.6)

    # connector lines
    running2 = 0.0
    for i, v in enumerate(values[:-1]):
        running2 += v
        ax.plot([i + 0.3, i + 0.7], [running2, running2],
                color="grey", linewidth=1, linestyle="--")

    pos_patch = mpatches.Patch(color="steelblue", label="Positive")
    neg_patch = mpatches.Patch(color="tomato", label="Negative")
    ax.legend(handles=[pos_patch, neg_patch])
    ax.tick_params(axis="x", rotation=35)


def _multi_line(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "multi_line")
    cols_y = [spec.y] if isinstance(spec.y, str) else list(spec.y or [])
    if not cols_y:
        raise ValueError("multi_line chart requires at least one y column")
    for col in cols_y:
        ax.plot(df[col_x], df[col], label=col, marker="o", markersize=3)
    ax.legend()


def _render_pair_plot(spec: ChartSpec) -> str:
    """Render a seaborn pair plot and save it."""
    try:
        import seaborn as sns
        cols = (
            [spec.x, spec.y] if spec.x and spec.y
            else spec.data.select_dtypes(include="number").columns.tolist()[:5]
        )
        hue = spec.hue if spec.hue and spec.hue in spec.data.columns else None
        palette = None if hue is None else None  # let seaborn choose
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            g = sns.pairplot(
                spec.data[cols + ([hue] if hue else [])],
                hue=hue,
                palette=palette,
                plot_kws={"alpha": 0.6},
                diag_kind="kde",
            )
        if spec.title:
            g.figure.suptitle(spec.title, y=1.02)
        g.figure.tight_layout()
        return _save(g.figure, spec)
    except ImportError:
        raise ImportError(
            "seaborn is required for pair_plot. Install it with: pip install seaborn"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _require(val, name: str, chart: str):
    if val is None:
        raise ValueError(f"'{name}' is required for chart_type='{chart}'")
    return val


def _default_title(spec: ChartSpec) -> str:
    parts = [spec.chart_type.replace("_", " ").title()]
    if spec.y:
        y_label = spec.y if isinstance(spec.y, str) else ", ".join(spec.y)
        parts.append(f"— {y_label}")
    return " ".join(parts)


def _save(fig: plt.Figure, spec: ChartSpec) -> str:
    """Save a figure to the output directory and return the absolute path."""
    output_dir = spec.output_dir or tempfile.mkdtemp(prefix="chu_charts_")
    os.makedirs(output_dir, exist_ok=True)
    safe_title = (spec.title or spec.chart_type).replace(" ", "_").lower()[:50]
    unique_id = uuid.uuid4().hex[:12]
    filepath = os.path.join(output_dir, f"{safe_title}_{unique_id}.png")
    fig.savefig(filepath, format="png", dpi=120, bbox_inches="tight")
    return os.path.abspath(filepath)
