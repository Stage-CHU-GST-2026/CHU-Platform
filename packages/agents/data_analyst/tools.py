"""Allowed tools for the Data Analyst agent."""

from tools.analytics import (
    AggregateTool,
    ComputeStatsTool,
    CorrelationTool,
    FilterTool,
    OutlierDetectionTool,
    SortTool,
)
from tools.cleaning import (
    DropColumnsTool,
    DuplicatesTool,
    MissingValuesTool,
)

from tools.duckdb_tools import (
    DuckDBAggregateTool,
    DuckDBFilterTool,
    DuckDBWindowStatsTool,
    QuerySQLTool,
)

from tools.inspection import (
    ColumnInfoTool,
    DatasetHeadTool,
    DatasetShapeTool,
    DatasetSummaryTool,
    DescribeDatasetTool,
    ListColumnsTool,
    ListDatasetsTool,
)
from tools.planning import CreateBlueprintTool
from tools.visualization import CorrelationHeatmapTool, GenerateChartTool

DATA_ANALYST_TOOLS = [
    # Discovery
    ListDatasetsTool(),
    # Inspection
    DescribeDatasetTool(),
    DatasetSummaryTool(),
    DatasetHeadTool(),
    DatasetShapeTool(),
    ListColumnsTool(),
    ColumnInfoTool(),
    # High-Performance DuckDB SQL Suite
    QuerySQLTool(),
    DuckDBAggregateTool(),
    DuckDBFilterTool(),
    DuckDBWindowStatsTool(),
    # Analytics & Statistics
    ComputeStatsTool(),
    AggregateTool(),
    FilterTool(),
    SortTool(),
    CorrelationTool(),
    OutlierDetectionTool(),
    # Cleaning
    MissingValuesTool(),
    DuplicatesTool(),
    DropColumnsTool(),
    # Visualization
    GenerateChartTool(),
    CorrelationHeatmapTool(),
    # Planning
    CreateBlueprintTool(),
]
