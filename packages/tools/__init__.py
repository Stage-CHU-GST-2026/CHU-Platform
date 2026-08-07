"""Tools — bridge between the AI framework and analysis logic."""

# isort: skip_file

from .registry import TOOL_REGISTRY, register_tool

from .inspection import (
    ColumnInfoTool,
    DatasetHeadTool,
    DatasetShapeTool,
    DatasetSummaryTool,
    DescribeDatasetTool,
    ListColumnsTool,
    ListDatasetsTool,
    register_datasets,
    clear_registered_datasets,
)

from .analytics import (
    AggregateTool,
    ComputeStatsTool,
    CorrelationTool,
    FilterTool,
    MaxTool,
    MeanTool,
    MedianTool,
    MinTool,
    OutlierDetectionTool,
    QuantilesTool,
    SortTool,
    StdTool,
)

from .cleaning import (
    DropColumnsTool,
    DuplicatesTool,
    MissingValuesTool,
)

from .visualization import (
    CHARTS_DIR,
    CHART_ARTIFACT_PREFIX,
    CHART_URL_PREFIX,
    CorrelationHeatmapTool,
    GenerateChartTool,
)

from .planning import (
    ARTIFACT_URL_PREFIX,
    CreateBlueprintTool,
)

_TOOL_CLASSES = [
    # Inspection
    DescribeDatasetTool,
    DatasetSummaryTool,
    DatasetHeadTool,
    DatasetShapeTool,
    ListColumnsTool,
    ColumnInfoTool,
    ListDatasetsTool,
    # Analytics & Statistics
    ComputeStatsTool,
    MeanTool,
    MedianTool,
    MinTool,
    MaxTool,
    StdTool,
    QuantilesTool,
    AggregateTool,
    FilterTool,
    SortTool,
    CorrelationTool,
    OutlierDetectionTool,
    # Cleaning
    MissingValuesTool,
    DuplicatesTool,
    DropColumnsTool,
    # Visualization
    GenerateChartTool,
    CorrelationHeatmapTool,
    # Planning
    CreateBlueprintTool,
]

for cls in _TOOL_CLASSES:
    register_tool(cls)

__all__ = [
    # Inspection
    "DescribeDatasetTool",
    "DatasetSummaryTool",
    "DatasetHeadTool",
    "DatasetShapeTool",
    "ListColumnsTool",
    "ColumnInfoTool",
    "ListDatasetsTool",
    "register_datasets",
    "clear_registered_datasets",
    # Analytics
    "ComputeStatsTool",
    "MeanTool",
    "MedianTool",
    "MinTool",
    "MaxTool",
    "StdTool",
    "QuantilesTool",
    "AggregateTool",
    "FilterTool",
    "SortTool",
    "CorrelationTool",
    "OutlierDetectionTool",
    # Cleaning
    "MissingValuesTool",
    "DuplicatesTool",
    "DropColumnsTool",
    # Visualization
    "GenerateChartTool",
    "CorrelationHeatmapTool",
    "CHARTS_DIR",
    "CHART_ARTIFACT_PREFIX",
    "CHART_URL_PREFIX",
    # Planning
    "CreateBlueprintTool",
    "ARTIFACT_URL_PREFIX",
    # Registry
    "TOOL_REGISTRY",
    "register_tool",
]
