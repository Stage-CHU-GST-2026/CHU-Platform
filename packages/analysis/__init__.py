"""Analysis engine — pure business logic.

No LangChain, LangGraph, or OpenAI dependencies.
Can be used standalone or imported by tools.
"""

from .engine import AnalysisEngine
from .profiler import ProfileResult, profile
from .statistics import describe, quantiles, correlation_matrix
from .charts import ChartSpec, ChartArtifact, render_chart, render_chart_artifact

__all__ = [
    "AnalysisEngine",
    "ProfileResult",
    "profile",
    "describe",
    "quantiles",
    "correlation_matrix",
    "ChartSpec",
    "ChartArtifact",
    "render_chart",
    "render_chart_artifact",
]
