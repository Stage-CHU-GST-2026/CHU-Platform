"""SQL tools — query loaded datasets with standard SQL via DuckDB.

Each dataset loaded by the AnalysisEngine is automatically registered
as a table whose name is derived from its filename (with dots/hyphens
replaced by underscores). The LLM can discover available tables, inspect
their schema, and run arbitrary SELECT queries.
"""

from __future__ import annotations

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from analysis.engine import AnalysisEngine

_engine = AnalysisEngine()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SQLQuerySchema(BaseModel):
    query: str = Field(
        description=(
            "SQL query to execute against loaded datasets. "
            "Use standard SQL syntax (DuckDB dialect). "
            "Table names are derived from dataset filenames — "
            "use `sql_tables` to discover available tables and "
            "`sql_schema` to inspect their columns before writing queries. "
            "Examples: SELECT * FROM sales WHERE revenue > 1000; "
            "SELECT category, SUM(amount) AS total FROM transactions GROUP BY category ORDER BY total DESC; "
            "SELECT a.name, b.total FROM customers a JOIN orders b ON a.id = b.customer_id;"
        )
    )


class SQLTableSchema(BaseModel):
    table: str = Field(
        description="Name of the table to describe (use `sql_tables` first to list available tables)."
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

class SQLQueryTool(BaseTool):
    name: str = "sql_query"
    description: str = (
        "Execute a SQL query against loaded datasets. "
        "Datasets are registered as tables automatically when loaded. "
        "Use `sql_tables` to list available tables and `sql_schema` "
        "to see column names and types before writing a query. "
        "Supports full SQL: SELECT, WHERE, GROUP BY, HAVING, ORDER BY, "
        "JOINs between datasets, subqueries, window functions, and aggregations."
    )
    args_schema: type[BaseModel] = SQLQuerySchema

    def _run(self, query: str) -> str:
        return _engine.sql_query(query)


class SQLTablesTool(BaseTool):
    name: str = "sql_tables"
    description: str = (
        "List all datasets currently available for SQL querying. "
        "Call this first before writing SQL queries to know which "
        "table names to use in FROM and JOIN clauses."
    )
    args_schema: type[BaseModel] = BaseModel

    def _run(self, **kwargs: str) -> str:
        return _engine.sql_tables()


class SQLSchemaTool(BaseTool):
    name: str = "sql_schema"
    description: str = (
        "Show the schema (column names, types, nullability) for a "
        "specific table. Call this before writing a SQL query to "
        "know which columns are available and their data types."
    )
    args_schema: type[BaseModel] = SQLTableSchema

    def _run(self, table: str) -> str:
        return _engine.sql_schema(table)


# ---------------------------------------------------------------------------
# Data exploration schemas
# ---------------------------------------------------------------------------

class SQLSampleSchema(BaseModel):
    table: str = Field(
        description="Name of the table to sample data from."
    )
    n: int = Field(
        default=10,
        description="Number of random rows to return (default: 10, max: 50).",
    )


class SQLStatsSchema(BaseModel):
    table: str = Field(
        description="Name of the table to compute statistics for."
    )
    columns: list[str] | None = Field(
        default=None,
        description="Specific numeric columns to analyze. If omitted, all numeric columns are used.",
    )


class SQLUniqueSchema(BaseModel):
    table: str = Field(
        description="Name of the table containing the column."
    )
    column: str = Field(
        description="Column name to get unique values for."
    )
    limit: int = Field(
        default=20,
        description="Maximum number of unique values to return (default: 20).",
    )


# ---------------------------------------------------------------------------
# Query analysis schemas
# ---------------------------------------------------------------------------

class SQLDuplicateSchema(BaseModel):
    table: str = Field(
        description="Name of the table to check for duplicates."
    )
    columns: list[str] | None = Field(
        default=None,
        description="Columns to check for duplicate values. If omitted, all columns are used.",
    )


class SQLCreateViewSchema(BaseModel):
    name: str = Field(
        description="Name for the new view (use snake_case, e.g. 'monthly_sales')."
    )
    query: str = Field(
        description="SELECT query that defines the view."
    )


class SQLExportSchema(BaseModel):
    query: str = Field(
        description="SELECT query whose results to export."
    )
    path: str = Field(
        description="Output file path (e.g. 'exports/results.csv', 'exports/data.parquet', 'exports/data.json')."
    )
    format: str = Field(
        default="csv",
        description="Export format: 'csv', 'parquet', or 'json' (default: csv).",
    )


class SQLCompareSchema(BaseModel):
    query1: str = Field(
        description="First SELECT query to compare."
    )
    query2: str = Field(
        description="Second SELECT query to compare against the first."
    )


class SQLDateRangeSchema(BaseModel):
    table: str = Field(
        description="Name of the table containing the date column."
    )
    column: str = Field(
        description="Name of the date or datetime column to analyze."
    )


class SQLPivotSchema(BaseModel):
    table: str = Field(
        description="Name of the table to pivot."
    )
    index: str = Field(
        description="Column to use as row labels (GROUP BY column)."
    )
    columns: str = Field(
        description="Column whose values become new column headers."
    )
    values: str = Field(
        description="Column to aggregate for the pivot values."
    )
    agg: str = Field(
        default="SUM",
        description="Aggregation function: SUM, COUNT, AVG, MIN, MAX, MEDIAN (default: SUM).",
    )


class SQLOutlierSchema(BaseModel):
    table: str = Field(
        description="Name of the table containing the numeric column."
    )
    column: str = Field(
        description="Numeric column to check for outliers."
    )
    method: str = Field(
        default="iqr",
        description="Detection method: 'iqr' (Inter-Quartile Range) or 'zscore' (default: iqr).",
    )
    threshold: float = Field(
        default=1.5,
        description="Threshold multiplier: 1.5 for IQR, 3.0 for Z-score (default: 1.5).",
    )


# ---------------------------------------------------------------------------
# Data exploration tools
# ---------------------------------------------------------------------------

class SQLSampleTool(BaseTool):
    """Get a sample of data from a table to preview its contents."""

    name: str = "sql_sample"
    description: str = (
        "Get a random sample of rows from a table to preview actual data values. "
        "Useful for understanding data distribution, formats, and quality "
        "before writing complex queries. Returns N random rows."
    )
    args_schema: type[BaseModel] = SQLSampleSchema

    def _run(self, table: str, n: int = 10) -> str:
        return _engine.sql_sample(table, n=min(n, 50))


class SQLStatsTool(BaseTool):
    """Get basic statistics for numeric columns."""

    name: str = "sql_stats"
    description: str = (
        "Compute basic statistics (count, mean, min, max, std, quartiles) for "
        "numeric columns in a table. Useful for understanding data "
        "distribution and identifying outliers or missing values."
    )
    args_schema: type[BaseModel] = SQLStatsSchema

    def _run(self, table: str, columns: list[str] | None = None) -> str:
        return _engine.sql_stats(table, columns)


class SQLUniqueTool(BaseTool):
    """Get unique values and counts for categorical columns."""

    name: str = "sql_unique"
    description: str = (
        "Get unique values and their frequencies for a specified column. "
        "Useful for understanding categorical data distributions, "
        "identifying categories, and detecting data quality issues."
    )
    args_schema: type[BaseModel] = SQLUniqueSchema

    def _run(self, table: str, column: str, limit: int = 20) -> str:
        return _engine.sql_unique(table, column, limit=min(limit, 100))


# ---------------------------------------------------------------------------
# Query analysis & debugging tools
# ---------------------------------------------------------------------------

class SQLExplainTool(BaseTool):
    """Get query execution plan."""

    name: str = "sql_explain"
    description: str = (
        "Show the execution plan for a query without running it. "
        "Useful for understanding how DuckDB will execute your query, "
        "identifying performance bottlenecks, and optimizing complex queries."
    )
    args_schema: type[BaseModel] = SQLQuerySchema

    def _run(self, query: str) -> str:
        return _engine.sql_explain(query)


class SQLValidateTool(BaseTool):
    """Validate SQL syntax without executing."""

    name: str = "sql_validate"
    description: str = (
        "Validate SQL syntax and check if table/column names exist "
        "without executing the query. Useful for testing queries "
        "safely before running them on large datasets."
    )
    args_schema: type[BaseModel] = SQLQuerySchema

    def _run(self, query: str) -> str:
        return _engine.sql_validate(query)


# ---------------------------------------------------------------------------
# Data quality tools
# ---------------------------------------------------------------------------

class SQLNullCheckTool(BaseTool):
    """Check for NULL values in columns."""

    name: str = "sql_nulls"
    description: str = (
        "Check for NULL values across columns in a table. Returns "
        "count and percentage of NULLs per column. Essential for "
        "data quality assessment and cleaning."
    )
    args_schema: type[BaseModel] = SQLTableSchema

    def _run(self, table: str) -> str:
        return _engine.sql_nulls(table)


class SQLDuplicateCheckTool(BaseTool):
    """Check for duplicate rows."""

    name: str = "sql_duplicates"
    description: str = (
        "Check for duplicate rows in a table based on specified columns. "
        "Returns count of duplicates and sample duplicate rows. "
        "Useful for data cleaning and deduplication."
    )
    args_schema: type[BaseModel] = SQLDuplicateSchema

    def _run(self, table: str, columns: list[str] | None = None) -> str:
        return _engine.sql_duplicates(table, columns)


# ---------------------------------------------------------------------------
# Data transformation tools
# ---------------------------------------------------------------------------

class SQLCreateViewTool(BaseTool):
    """Create a view for complex queries."""

    name: str = "sql_create_view"
    description: str = (
        "Create a persistent view from a SELECT query. Useful for "
        "encapsulating complex logic, reusing common transformations, "
        "and breaking down large analyses into manageable steps."
    )
    args_schema: type[BaseModel] = SQLCreateViewSchema

    def _run(self, name: str, query: str) -> str:
        return _engine.sql_create_view(name, query)


class SQLExportTool(BaseTool):
    """Export query results to a file."""

    name: str = "sql_export"
    description: str = (
        "Export the results of a query to a file (CSV, Parquet, or JSON). "
        "Useful for saving results for external tools or creating reports."
    )
    args_schema: type[BaseModel] = SQLExportSchema

    def _run(self, query: str, path: str, format: str = "csv") -> str:
        return _engine.sql_export(query, path, format)


# ---------------------------------------------------------------------------
# Comparison & diff tools
# ---------------------------------------------------------------------------

class SQLCompareTablesTool(BaseTool):
    """Compare two tables or query results."""

    name: str = "sql_compare"
    description: str = (
        "Compare two tables or query results to find differences. "
        "Returns rows that are in one but not the other, and "
        "rows that are common. Useful for data validation and "
        "auditing data changes."
    )
    args_schema: type[BaseModel] = SQLCompareSchema

    def _run(self, query1: str, query2: str) -> str:
        return _engine.sql_compare(query1, query2)


# ---------------------------------------------------------------------------
# Time intelligence tools
# ---------------------------------------------------------------------------

class SQLDateRangeTool(BaseTool):
    """Get date range and distribution for date columns."""

    name: str = "sql_date_range"
    description: str = (
        "Get date range (min/max) and distribution over time for "
        "date/datetime columns. Useful for understanding time coverage, "
        "identifying time gaps, and planning time-based analyses."
    )
    args_schema: type[BaseModel] = SQLDateRangeSchema

    def _run(self, table: str, column: str) -> str:
        return _engine.sql_date_range(table, column)


# ---------------------------------------------------------------------------
# Metadata & dependency tools
# ---------------------------------------------------------------------------

class SQLTableDependenciesTool(BaseTool):
    """Show table relationships and potential JOIN keys."""

    name: str = "sql_dependencies"
    description: str = (
        "Analyze table relationships by identifying potential join keys "
        "(columns with same name, similar data types, or high value overlap). "
        "Useful for understanding dataset relationships before writing JOIN queries."
    )
    args_schema: type[BaseModel] = BaseModel

    def _run(self, **kwargs: str) -> str:
        return _engine.sql_dependencies()


class SQLTableSizeTool(BaseTool):
    """Get table size and row count estimates."""

    name: str = "sql_size"
    description: str = (
        "Get estimated table size (rows, columns, memory usage). "
        "Useful for planning query execution and understanding "
        "dataset scale before running resource-intensive operations."
    )
    args_schema: type[BaseModel] = SQLTableSchema

    def _run(self, table: str) -> str:
        return _engine.sql_size(table)


# ---------------------------------------------------------------------------
# Query history tool
# ---------------------------------------------------------------------------

class SQLHistoryTool(BaseTool):
    """Show recent query history."""

    name: str = "sql_history"
    description: str = (
        "Show recently executed SQL queries. Useful for tracking analysis "
        "progression, reusing previous work, and debugging issues."
    )
    args_schema: type[BaseModel] = BaseModel

    def _run(self, **kwargs: str) -> str:
        return _engine.sql_history()


# ---------------------------------------------------------------------------
# Pivot & aggregation tools
# ---------------------------------------------------------------------------

class SQLPivotTool(BaseTool):
    """Create pivot/crosstab reports."""

    name: str = "sql_pivot"
    description: str = (
        "Create a pivot table (crosstab) from your data. Converts "
        "row values into columns with aggregations. Useful for "
        "creating summary reports and data visualization preparation."
    )
    args_schema: type[BaseModel] = SQLPivotSchema

    def _run(
        self,
        table: str,
        index: str,
        columns: str,
        values: str,
        agg: str = "SUM",
    ) -> str:
        return _engine.sql_pivot(table, index, columns, values, agg)


# ---------------------------------------------------------------------------
# Outlier detection
# ---------------------------------------------------------------------------

class SQLOutlierTool(BaseTool):
    """Detect outliers in numeric columns."""

    name: str = "sql_outliers"
    description: str = (
        "Detect statistical outliers in numeric columns using IQR or "
        "Z-score methods. Useful for data cleaning and identifying "
        "unusual values that might indicate data entry errors."
    )
    args_schema: type[BaseModel] = SQLOutlierSchema

    def _run(
        self,
        table: str,
        column: str,
        method: str = "iqr",
        threshold: float = 1.5,
    ) -> str:
        return _engine.sql_outliers(table, column, method, threshold)
