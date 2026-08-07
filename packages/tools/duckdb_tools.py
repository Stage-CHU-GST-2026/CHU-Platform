"""DuckDB Multi-Task Tool Suite — vectorized SQL query engine for AI data agents."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import duckdb
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class QuerySQLSchema(BaseModel):
    sql_query: str = Field(
        description=(
            "Standard ANSI SQL query to execute using DuckDB. "
            "Refer to dataset files directly using single quotes, e.g. "
            "SELECT * FROM 'data/sales.csv' WHERE region = 'US' ORDER BY amount DESC LIMIT 50. "
            "Supports multi-table JOINs, CTEs (WITH clause), window functions, "
            "and GROUP BY ALL."
        )
    )
    max_rows: int = Field(
        default=100,
        description="Maximum number of rows to return in the markdown table output (default: 100).",
    )


class DuckDBAggregateSchema(BaseModel):
    path: str = Field(description="Path to the dataset file (CSV, Parquet, Excel, etc.).")
    group_by: str = Field(
        description="Comma-separated column names to group by, e.g. 'category, region'."
    )
    aggregations: str = Field(
        description=(
            "Comma-separated list of SQL aggregate expressions, e.g. "
            "'SUM(sales) AS total_sales, AVG(price) AS avg_price, COUNT(*) AS cnt'."
        )
    )
    having: Optional[str] = Field(
        default=None,
        description="Optional SQL HAVING filter expression, e.g. 'COUNT(*) > 10'.",
    )
    order_by: Optional[str] = Field(
        default=None,
        description="Optional SQL ORDER BY expression, e.g. 'total_sales DESC'.",
    )
    limit: int = Field(
        default=50, description="Maximum rows to return (default: 50)."
    )


class DuckDBFilterSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    where_clause: str = Field(
        description="SQL WHERE expression, e.g. 'age > 30 AND status = \"active\"'."
    )
    select_columns: Optional[str] = Field(
        default="*",
        description="Comma-separated columns to select (default: '*' for all columns).",
    )
    limit: int = Field(
        default=50, description="Maximum rows to return (default: 50)."
    )


class DuckDBWindowStatsSchema(BaseModel):
    path: str = Field(description="Path to the dataset file.")
    partition_by: str = Field(
        description="Column(s) to partition window function by, e.g. 'department'."
    )
    order_by: str = Field(
        description="Column(s) to order window function by, e.g. 'salary DESC'."
    )
    window_function: str = Field(
        description=(
            "SQL window function expression, e.g. "
            "'RANK()', 'DENSE_RANK()', 'ROW_NUMBER()', 'SUM(sales)', "
            "'LAG(price, 1)'."
        )
    )
    limit: int = Field(
        default=50, description="Maximum rows to return (default: 50)."
    )


# ---------------------------------------------------------------------------
# Helper: Safe Execution
# ---------------------------------------------------------------------------


def _execute_duckdb_sql(sql_query: str, max_rows: int = 100) -> str:
    """Execute a DuckDB SQL query safely and format the output."""
    try:
        conn = duckdb.connect(database=":memory:")
        rel = conn.sql(sql_query)
        if rel is None:
            return "Query executed successfully. (No output returned)"

        total_count = rel.count("*").fetchone()[0]
        df = rel.limit(max_rows).df()

        lines = [f"### SQL Query Result ({total_count:,} rows total, displaying top {len(df)}):"]
        try:
            lines.append(df.to_markdown(index=False))
        except Exception:
            lines.append(df.to_string(index=False))
        conn.close()
        return "\n".join(lines)
    except Exception as e:
        return f"DuckDB SQL Execution Error: {str(e)}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


class QuerySQLTool(BaseTool):
    name: str = "query_sql"
    description: str = (
        "Execute raw, high-performance ANSI SQL queries using DuckDB directly against dataset files "
        "(CSV, Parquet, JSON, Excel). "
        "Supports multi-table JOINs, subqueries, CTEs (WITH clause), window functions, "
        "GROUP BY ALL, and filtering. "
        "Reference files directly by path in SQL statements (e.g. `SELECT * FROM 'data/sales.csv'`)."
    )
    args_schema: type[BaseModel] = QuerySQLSchema

    def _run(self, sql_query: str, max_rows: int = 100) -> str:
        return _execute_duckdb_sql(sql_query, max_rows=max_rows)


class DuckDBAggregateTool(BaseTool):
    name: str = "duckdb_aggregate"
    description: str = (
        "High-performance vectorized group-by aggregation using DuckDB SQL engine. "
        "Fast for large datasets and complex multi-metric aggregations."
    )
    args_schema: type[BaseModel] = DuckDBAggregateSchema

    def _run(
        self,
        path: str,
        group_by: str,
        aggregations: str,
        having: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: int = 50,
    ) -> str:
        sql = f"SELECT {group_by}, {aggregations} FROM '{path}' GROUP BY {group_by}"
        if having:
            sql += f" HAVING {having}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        else:
            sql += f" ORDER BY {group_by}"
        sql += f" LIMIT {limit}"

        return _execute_duckdb_sql(sql, max_rows=limit)


class DuckDBFilterTool(BaseTool):
    name: str = "duckdb_filter"
    description: str = (
        "Filter a dataset using DuckDB SQL WHERE expressions. "
        "Extremely fast and handles large datasets without high memory usage."
    )
    args_schema: type[BaseModel] = DuckDBFilterSchema

    def _run(
        self,
        path: str,
        where_clause: str,
        select_columns: Optional[str] = "*",
        limit: int = 50,
    ) -> str:
        cols = select_columns if select_columns else "*"
        sql = f"SELECT {cols} FROM '{path}' WHERE {where_clause} LIMIT {limit}"
        return _execute_duckdb_sql(sql, max_rows=limit)


class DuckDBWindowStatsTool(BaseTool):
    name: str = "duckdb_window_stats"
    description: str = (
        "Compute analytical window functions (RANK, DENSE_RANK, ROW_NUMBER, LAG, LEAD, cumulative sums) "
        "over partitions of a dataset using DuckDB."
    )
    args_schema: type[BaseModel] = DuckDBWindowStatsSchema

    def _run(
        self,
        path: str,
        partition_by: str,
        order_by: str,
        window_function: str,
        limit: int = 50,
    ) -> str:
        sql = (
            f"SELECT *, {window_function} OVER (PARTITION BY {partition_by} ORDER BY {order_by}) AS window_result "
            f"FROM '{path}' LIMIT {limit}"
        )
        return _execute_duckdb_sql(sql, max_rows=limit)
