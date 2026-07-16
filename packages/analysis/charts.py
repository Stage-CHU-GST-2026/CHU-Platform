"""Chart generation — produces PNG chart files.

No AI dependencies. Uses matplotlib (and optionally seaborn) under the hood.

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
from dataclasses import dataclass, field
from typing import Literal

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd

matplotlib.use("Agg")

# ---------------------------------------------------------------------------
# Premium global aesthetics — applied once at import time
# ---------------------------------------------------------------------------

PALETTE = [
    "#6366f1",  # indigo
    "#ec4899",  # pink
    "#14b8a6",  # teal
    "#f59e0b",  # amber
    "#3b82f6",  # blue
    "#10b981",  # emerald
    "#f43f5e",  # rose
    "#8b5cf6",  # violet
    "#06b6d4",  # cyan
    "#84cc16",  # lime
]

_STYLE: dict = {
    "figure.facecolor": "#0f172a",
    "axes.facecolor": "#1e293b",
    "axes.edgecolor": "#334155",
    "axes.labelcolor": "#e2e8f0",
    "axes.titlecolor": "#f8fafc",
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlepad": 14,
    "axes.grid": True,
    "axes.prop_cycle": matplotlib.cycler(color=PALETTE),
    "grid.color": "#334155",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.5,
    "xtick.color": "#94a3b8",
    "ytick.color": "#94a3b8",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.facecolor": "#1e293b",
    "legend.edgecolor": "#334155",
    "legend.labelcolor": "#e2e8f0",
    "legend.fontsize": 9,
    "text.color": "#e2e8f0",
    "figure.dpi": 150,
}

matplotlib.rcParams.update(_STYLE)


# ---------------------------------------------------------------------------
# Chart type literal
# ---------------------------------------------------------------------------

ChartType = Literal[
    # ── original ──────────────────────────────────────────────────────────
    "bar",
    "line",
    "histogram",
    "scatter",
    "pie",
    "box",
    # ── newly added ───────────────────────────────────────────────────────
    "heatmap",
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
    figsize: tuple[int, int] = (11, 6)
    output_dir: str | None = None

    # --- extended parameters ------------------------------------------------
    # grouping / hue column (violin, grouped_bar, stacked_bar)
    hue: str | None = None
    # third numeric column driving bubble size
    size_col: str | None = None
    # bins for histogram / kde
    bins: int | None = None
    # extra kwargs forwarded to the underlying plot call
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
            ax.set_xlabel(spec.xlabel, fontsize=11)
        if spec.ylabel:
            ax.set_ylabel(spec.ylabel, fontsize=11)
        fig.tight_layout(pad=2.0)
    finally:
        plt.close(fig)

    return _save(fig, spec)


# ---------------------------------------------------------------------------
# Internal: dispatch
# ---------------------------------------------------------------------------


def _draw(ax: plt.Axes, spec: ChartSpec) -> None:  # noqa: PLR0912
    """Dispatch to the correct plotting function."""
    df = spec.data
    ct = spec.chart_type

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
# Chart implementations
# ---------------------------------------------------------------------------


def _bar(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "bar")
    col_y = _require(spec.y, "y", "bar")
    bars = ax.bar(df[col_x].astype(str), df[col_y], color=PALETTE[0],
                  edgecolor="#0f172a", linewidth=0.8)
    _label_bars(ax, bars, orientation="v")
    ax.tick_params(axis="x", rotation=35)


def _line(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "line")
    col_y = _require(spec.y, "y", "line")
    ax.plot(df[col_x], df[col_y], color=PALETTE[0], linewidth=2,
            marker="o", markersize=4, markerfacecolor="#0f172a")
    ax.fill_between(df[col_x], df[col_y], alpha=0.15, color=PALETTE[0])


def _histogram(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col = spec.y or spec.x
    col = _require(col, "x or y", "histogram")
    bins = spec.bins or "auto"
    n, bins_out, patches = ax.hist(df[col], bins=bins, color=PALETTE[0],
                                   edgecolor="#0f172a", linewidth=0.6)
    # gradient fill
    for i, patch in enumerate(patches):
        patch.set_facecolor(PALETTE[i % len(PALETTE)])


def _scatter(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "scatter")
    col_y = _require(spec.y, "y", "scatter")
    ax.scatter(df[col_x], df[col_y], color=PALETTE[0], alpha=0.75,
               edgecolors="#0f172a", linewidths=0.5, s=60)


def _pie(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_label = _require(spec.x, "x", "pie")
    col_val = _require(spec.y, "y", "pie")
    wedges, texts, autotexts = ax.pie(
        df[col_val],
        labels=df[col_label].astype(str),
        colors=PALETTE[: len(df)],
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "#0f172a", "linewidth": 1.2},
    )
    for at in autotexts:
        at.set_color("#f8fafc")
        at.set_fontsize(9)
    ax.set_aspect("equal")


def _box(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    cols = spec.y or spec.x
    cols = [cols] if isinstance(cols, str) else list(
        cols)  # type: ignore[arg-type]
    data = [df[c].dropna() for c in cols]
    bp = ax.boxplot(data, tick_labels=cols, patch_artist=True,
                    medianprops={"color": "#f8fafc", "linewidth": 2})

    for i, patch in enumerate(bp["boxes"]):
        patch.set_facecolor(PALETTE[i % len(PALETTE)])
        patch.set_alpha(0.8)


def _heatmap(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    numeric_df = df.select_dtypes(include="number")
    img = ax.imshow(numeric_df.values, cmap="plasma", aspect="auto")
    plt.colorbar(img, ax=ax, fraction=0.03, pad=0.02)
    ax.set_xticks(range(len(numeric_df.columns)))
    ax.set_xticklabels(numeric_df.columns, rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(numeric_df.index)))
    ax.set_yticklabels(numeric_df.index, fontsize=9)
    for i in range(len(numeric_df.index)):
        for j in range(len(numeric_df.columns)):
            ax.text(j, i, f"{numeric_df.values[i, j]:.2f}",
                    ha="center", va="center", fontsize=7.5, color="#f8fafc")


def _area(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "area")
    cols_y = [spec.y] if isinstance(spec.y, str) else list(spec.y or [])
    if not cols_y:
        raise ValueError("area chart requires at least one y column")
    for i, col in enumerate(cols_y):
        ax.fill_between(df[col_x], df[col], alpha=0.55,
                        color=PALETTE[i % len(PALETTE)], label=col)
        ax.plot(df[col_x], df[col], color=PALETTE[i % len(PALETTE)],
                linewidth=1.5, alpha=0.9)
    if len(cols_y) > 1:
        ax.legend()


def _kde(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col = spec.y or spec.x
    col = _require(col, "x or y", "kde")
    try:
        import seaborn as sns  # optional soft dependency
        sns.kdeplot(data=df, x=col, ax=ax,
                    fill=True, color=PALETTE[0], alpha=0.5, linewidth=2)
    except ImportError:
        # pure-numpy fallback using a Gaussian kernel
        from scipy.stats import gaussian_kde  # type: ignore[import]
        vals = df[col].dropna().values
        kde = gaussian_kde(vals)
        xs = np.linspace(vals.min(), vals.max(), 300)
        ax.plot(xs, kde(xs), color=PALETTE[0], linewidth=2)
        ax.fill_between(xs, kde(xs), alpha=0.35, color=PALETTE[0])


def _violin(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_y = _require(spec.y, "y", "violin")
    try:
        import seaborn as sns
        sns.violinplot(
            data=df,
            x=spec.hue if spec.hue else None,
            y=col_y,
            hue=spec.hue if spec.hue else None,
            ax=ax,
            palette=PALETTE[: df[spec.hue].nunique(
            )] if spec.hue and spec.hue in df.columns else None,
            inner="box",
            linewidth=1.2,
            legend=False,
        )
    except ImportError:
        # fallback: grouped matplotlib violinplot
        if spec.hue and spec.hue in df.columns:
            groups = [grp[col_y].dropna().values
                      for _, grp in df.groupby(spec.hue)]
            labels = [str(k) for k, _ in df.groupby(spec.hue)]
        else:
            groups = [df[col_y].dropna().values]
            labels = [col_y]
        vp = ax.violinplot(groups, showmedians=True)
        ax.set_xticks(range(1, len(labels) + 1))
        ax.set_xticklabels(labels, rotation=30)
        for i, body in enumerate(vp["bodies"]):
            body.set_facecolor(PALETTE[i % len(PALETTE)])
            body.set_alpha(0.75)


def _stacked_bar(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "stacked_bar")
    hue_col = spec.hue or _require(None, "hue", "stacked_bar")
    val_col = _require(spec.y, "y", "stacked_bar")
    pivot = df.pivot_table(index=col_x, columns=hue_col,
                           values=val_col, aggfunc="sum", fill_value=0)
    bottom = np.zeros(len(pivot))
    for i, col in enumerate(pivot.columns):
        bars = ax.bar(pivot.index.astype(str), pivot[col],
                      bottom=bottom, label=str(col),
                      color=PALETTE[i % len(PALETTE)],
                      edgecolor="#0f172a", linewidth=0.6)
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
        ax.bar(xs + offset, pivot[col], width=width * 0.9,
               label=str(col), color=PALETTE[i % len(PALETTE)],
               edgecolor="#0f172a", linewidth=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels(pivot.index.astype(str), rotation=35)
    ax.legend(title=hue_col)


def _count_bar(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col = spec.x or spec.y
    col = _require(col, "x", "count_bar")
    counts = df[col].value_counts().sort_values(ascending=True)
    bars = ax.barh(counts.index.astype(str), counts.values,
                   color=[PALETTE[i % len(PALETTE)]
                          for i in range(len(counts))],
                   edgecolor="#0f172a", linewidth=0.6)
    for bar in bars:
        width = bar.get_width()
        ax.text(width + counts.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{int(width):,}", va="center", fontsize=8.5, color="#e2e8f0")


def _bubble(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "bubble")
    col_y = _require(spec.y, "y", "bubble")
    size_col = spec.size_col
    if size_col and size_col in df.columns:
        raw = df[size_col].fillna(0)
        sizes = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9) * 900 + 30
    else:
        sizes = 80
    sc = ax.scatter(df[col_x], df[col_y], s=sizes,
                    c=PALETTE[0], alpha=0.7, edgecolors="#0f172a",
                    linewidths=0.5)
    if size_col:
        ax.set_title((spec.title or "Bubble Chart") + f"  (size ∝ {size_col})")


def _funnel(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_label = _require(spec.x, "x", "funnel")
    col_val = _require(spec.y, "y", "funnel")
    data = df[[col_label, col_val]].sort_values(col_val, ascending=False)
    max_val = data[col_val].max()
    for i, (_, row) in enumerate(data.iterrows()):
        width = row[col_val] / max_val
        center = 0.5
        left = center - width / 2
        ax.barh(i, width, left=left, height=0.7,
                color=PALETTE[i % len(PALETTE)],
                edgecolor="#0f172a", linewidth=0.8)
        ax.text(center, i, f"{row[col_label]}  ({row[col_val]:,.0f})",
                ha="center", va="center", fontsize=9.5, color="#f8fafc",
                fontweight="bold")
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
            colors.append(PALETTE[2])   # teal = positive
        else:
            bottoms.append(running + v)
            tops.append(-v)
            colors.append(PALETTE[6])   # rose = negative
        running += v

    ax.bar(labels, tops, bottom=bottoms, color=colors,
           edgecolor="#0f172a", linewidth=0.8, width=0.6)

    # connector lines
    running2 = 0.0
    for i, v in enumerate(values[:-1]):
        running2 += v
        ax.plot([i + 0.3, i + 0.7], [running2, running2],
                color="#94a3b8", linewidth=1, linestyle="--")

    pos_patch = mpatches.Patch(color=PALETTE[2], label="Positive")
    neg_patch = mpatches.Patch(color=PALETTE[6], label="Negative")
    ax.legend(handles=[pos_patch, neg_patch], loc="upper right")
    ax.tick_params(axis="x", rotation=35)


def _multi_line(ax: plt.Axes, df: pd.DataFrame, spec: ChartSpec) -> None:
    col_x = _require(spec.x, "x", "multi_line")
    cols_y = [spec.y] if isinstance(spec.y, str) else list(spec.y or [])
    if not cols_y:
        raise ValueError("multi_line chart requires at least one y column")
    for i, col in enumerate(cols_y):
        ax.plot(df[col_x], df[col], color=PALETTE[i % len(PALETTE)],
                linewidth=2, label=col,
                marker="o", markersize=3, markerfacecolor="#0f172a")
    ax.legend()


def _render_pair_plot(spec: ChartSpec) -> str:
    """Render a seaborn pair plot and save it."""
    import warnings
    try:
        import seaborn as sns
        sns.set_theme(style="darkgrid", rc={
            "axes.facecolor": "#1e293b",
            "figure.facecolor": "#0f172a",
            "axes.labelcolor": "#e2e8f0",
            "text.color": "#e2e8f0",
            "grid.color": "#334155",
        })
        cols = ([spec.x, spec.y] if spec.x and spec.y
                else spec.data.select_dtypes(include="number").columns.tolist()[:5])
        hue = spec.hue if spec.hue and spec.hue in spec.data.columns else None
        palette = PALETTE[:4] if hue else None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            g = sns.pairplot(spec.data[cols + ([hue] if hue else [])],
                             hue=hue, palette=palette,
                             plot_kws={"alpha": 0.6, "edgecolor": "none"},
                             diag_kind="kde")
        g.figure.suptitle(spec.title or "Pair Plot", y=1.02,
                          color="#f8fafc", fontsize=14, fontweight="bold")
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


def _label_bars(ax: plt.Axes, bars, orientation: str = "v") -> None:
    """Add value labels to bar charts."""
    for bar in bars:
        if orientation == "v":
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h * 1.01,
                    f"{h:,.1f}", ha="center", va="bottom", fontsize=8,
                    color="#e2e8f0")
        else:
            w = bar.get_width()
            ax.text(w * 1.01, bar.get_y() + bar.get_height() / 2,
                    f"{w:,.1f}", ha="left", va="center", fontsize=8,
                    color="#e2e8f0")


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
    fig.savefig(filepath, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    return os.path.abspath(filepath)
