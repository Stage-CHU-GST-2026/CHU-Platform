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
from .visualization import GenerateChartTool, CorrelationHeatmapTool
from .sql import (
    SQLQueryTool,
    SQLSchemaTool,
    SQLTablesTool,
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
    GenerateChartTool,
    CorrelationHeatmapTool,
    # SQL
    SQLQueryTool,
    SQLSchemaTool,
    SQLTablesTool,
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
    "GenerateChartTool",
    "CorrelationHeatmapTool",
    "SQLQueryTool",
    "SQLSchemaTool",
    "SQLTablesTool",
    "TOOL_REGISTRY",
    "register_tool",
]
