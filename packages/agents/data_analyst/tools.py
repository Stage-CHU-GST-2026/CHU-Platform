"""Allowed tools for the Data Analyst agent.

Only tools listed here can be used by this agent.
"""

from tools.inspection import (
    ColumnInfoTool,
    DatasetHeadTool,
    DatasetShapeTool,
    DatasetSummaryTool,
    DescribeDatasetTool,
    ListColumnsTool,
    ListDatasetsTool,
)
from tools.statistics import (
    ComputeStatsTool,
)
from tools.cleaning import (
    DropColumnsTool,
    DuplicatesTool,
    MissingValuesTool,
)
from tools.aggregation import (
    AggregateTool,
    FilterTool,
    SortTool,
)
from tools.relationships import (
    CorrelationTool,
    OutlierDetectionTool,
)
from tools.visualization import GenerateChartTool, CorrelationHeatmapTool
from tools.planning import CreateBlueprintTool

DATA_ANALYST_TOOLS = [
    # Discovery — call this first when no dataset is known
    ListDatasetsTool(),
    # Inspection
    DescribeDatasetTool(),
    DatasetSummaryTool(),
    DatasetHeadTool(),
    DatasetShapeTool(),
    ListColumnsTool(),
    ColumnInfoTool(),
    # Statistics (consolidated single multi-metric tool to prevent tool spam)
    ComputeStatsTool(),
    # Cleaning
    MissingValuesTool(),
    DuplicatesTool(),
    DropColumnsTool(),
    # Aggregation
    AggregateTool(),
    FilterTool(),
    SortTool(),
    # Relationships
    CorrelationTool(),
    OutlierDetectionTool(),
    # Visualization
    GenerateChartTool(),
    CorrelationHeatmapTool(),
    # Planning
    CreateBlueprintTool(),
]
