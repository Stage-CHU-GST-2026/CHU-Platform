"""SQL analysis tools.

Groups:
  - Core:            query execution, table discovery, schema inspection
  - Exploration:     data preview, statistics, unique values
  - Query analysis:  EXPLAIN plans, syntax validation
  - Data quality:    NULL checks, duplicate detection
  - Transformation:  create views, export results
  - Comparison:      diff two query results
  - Time:            date range & distribution
  - Metadata:        table relationships, size estimates
  - History:         recent query log
  - Aggregation:     pivot / crosstab reports
  - Anomaly:         outlier detection (IQR / Z-score)
"""

from .sql import (
    # --- Core ---
    SQLQueryTool,          # execute arbitrary SQL queries
    SQLSchemaTool,         # show column names, types, nullability
    SQLTablesTool,         # list all available tables
    # --- Data exploration ---
    SQLSampleTool,         # random row preview of a table
    SQLStatsTool,          # count, mean, min, max, std, quartiles
    SQLUniqueTool,         # unique values + frequency distribution
    # --- Query analysis & debugging ---
    SQLExplainTool,        # DuckDB execution plan (EXPLAIN)
    SQLValidateTool,       # validate syntax without executing
    # --- Data quality ---
    SQLNullCheckTool,      # NULL count & percentage per column
    SQLDuplicateCheckTool, # find duplicate rows with sample groups
    # --- Data transformation ---
    SQLCreateViewTool,     # CREATE OR REPLACE VIEW from a SELECT
    SQLExportTool,         # export results to CSV / Parquet / JSON
    # --- Comparison ---
    SQLCompareTablesTool,  # set-diff two query results
    # --- Time intelligence ---
    SQLDateRangeTool,      # min/max dates, monthly distribution
    # --- Metadata & dependencies ---
    SQLTableDependenciesTool,  # auto-discover join keys between tables
    SQLTableSizeTool,          # row count, column count, memory estimate
    # --- History ---
    SQLHistoryTool,        # recently executed queries
    # --- Aggregation & pivot ---
    SQLPivotTool,          # pivot table (crosstab) reports
    # --- Anomaly detection ---
    SQLOutlierTool,        # IQR / Z-score outlier detection
)

__all__ = [
    # Core
    "SQLQueryTool",
    "SQLSchemaTool",
    "SQLTablesTool",
    # Data exploration
    "SQLSampleTool",
    "SQLStatsTool",
    "SQLUniqueTool",
    # Query analysis & debugging
    "SQLExplainTool",
    "SQLValidateTool",
    # Data quality
    "SQLNullCheckTool",
    "SQLDuplicateCheckTool",
    # Data transformation
    "SQLCreateViewTool",
    "SQLExportTool",
    # Comparison
    "SQLCompareTablesTool",
    # Time intelligence
    "SQLDateRangeTool",
    # Metadata & dependencies
    "SQLTableDependenciesTool",
    "SQLTableSizeTool",
    # History
    "SQLHistoryTool",
    # Aggregation & pivot
    "SQLPivotTool",
    # Anomaly detection
    "SQLOutlierTool",
]
