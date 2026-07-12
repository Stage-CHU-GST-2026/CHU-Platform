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
)
from tools.statistics import (
    MaxTool,
    MeanTool,
    MedianTool,
    MinTool,
    QuantilesTool,
    StdTool,
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
from tools.visualization import (
    BarChartTool,
    HistogramTool,
    LineChartTool,
    ScatterPlotTool,
)

DATA_ANALYST_TOOLS = [
    # Inspection
    DescribeDatasetTool(),
    DatasetSummaryTool(),
    DatasetHeadTool(),
    DatasetShapeTool(),
    ListColumnsTool(),
    ColumnInfoTool(),
    # Statistics
    MeanTool(),
    MedianTool(),
    MinTool(),
    MaxTool(),
    StdTool(),
    QuantilesTool(),
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
    BarChartTool(),
    HistogramTool(),
    ScatterPlotTool(),
    LineChartTool(),
]
