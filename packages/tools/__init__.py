"""Tools — bridge between the AI framework and analysis logic.

Each tool wraps one function from the analysis engine.
The LLM calls tools; tools call analysis; results go back to the LLM.
"""

# isort: skip_file

from .registry import TOOL_REGISTRY, register_tool

from .inspection import (
    ColumnInfoTool,
    DatasetHeadTool,
    DatasetShapeTool,
    DatasetSummaryTool,
    DescribeDatasetTool,
    ListColumnsTool,
)
from .statistics import (
    MaxTool,
    MeanTool,
    MedianTool,
    MinTool,
    QuantilesTool,
    StdTool,
)
from .cleaning import (
    DropColumnsTool,
    DuplicatesTool,
    MissingValuesTool,
)
from .aggregation import (
    AggregateTool,
    FilterTool,
    SortTool,
)
from .relationships import (
    CorrelationTool,
    OutlierDetectionTool,
)
from .visualization import (
    BarChartTool,
    HistogramTool,
    LineChartTool,
    ScatterPlotTool,
)

# ---------------------------------------------------------------------------
# Register all tools so they can be discovered by name
# ---------------------------------------------------------------------------

_TOOL_CLASSES = [
    # Inspection
    DescribeDatasetTool,
    DatasetSummaryTool,
    DatasetHeadTool,
    DatasetShapeTool,
    ListColumnsTool,
    ColumnInfoTool,
    # Statistics
    MeanTool,
    MedianTool,
    MinTool,
    MaxTool,
    StdTool,
    QuantilesTool,
    # Cleaning
    MissingValuesTool,
    DuplicatesTool,
    DropColumnsTool,
    # Aggregation
    AggregateTool,
    FilterTool,
    SortTool,
    # Relationships
    CorrelationTool,
    OutlierDetectionTool,
    # Visualization
    BarChartTool,
    HistogramTool,
    ScatterPlotTool,
    LineChartTool,
]

for cls in _TOOL_CLASSES:
    register_tool(cls)


__all__ = [
    "DescribeDatasetTool",
    "DatasetSummaryTool",
    "DatasetHeadTool",
    "DatasetShapeTool",
    "ListColumnsTool",
    "ColumnInfoTool",
    "MeanTool",
    "MedianTool",
    "MinTool",
    "MaxTool",
    "StdTool",
    "QuantilesTool",
    "MissingValuesTool",
    "DuplicatesTool",
    "DropColumnsTool",
    "AggregateTool",
    "FilterTool",
    "SortTool",
    "CorrelationTool",
    "OutlierDetectionTool",
    "BarChartTool",
    "HistogramTool",
    "ScatterPlotTool",
    "LineChartTool",
    "TOOL_REGISTRY",
    "register_tool",
]
