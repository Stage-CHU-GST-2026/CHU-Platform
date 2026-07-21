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
