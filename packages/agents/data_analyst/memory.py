"""Memory backend configuration and factory functions for Data Analyst agent."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from enum import Enum
from typing import AsyncIterator, Literal, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.base import BaseStore

load_dotenv()


def _default_pg_url() -> str:
    """Build the Postgres connection string from DATABASE_URL."""
    url = os.getenv("DATABASE_URL", "")
    if url:
        for prefix in ("+asyncpg", "+psycopg"):
            url = url.replace(prefix, "")
        if "?sslmode" not in url:
            url += "?sslmode=disable"
        return url

    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "postgres")
    password = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "app")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}?sslmode=disable"


class MemoryKind(str, Enum):
    """Supported memory backends."""
    INMEMORY = "inmemory"
    POSTGRES = "postgres"


class MemoryConfig(BaseModel):
    """Base class for all memory configurations."""
    kind: MemoryKind


class InMemoryConfig(MemoryConfig):
    """In-memory conversation memory (default)."""
    kind: Literal[MemoryKind.INMEMORY] = MemoryKind.INMEMORY


class PostgresConfig(MemoryConfig):
    """PostgreSQL-backed conversation memory."""
    kind: Literal[MemoryKind.POSTGRES] = MemoryKind.POSTGRES

    connection_string: str = Field(
        default_factory=_default_pg_url,
        description="PostgreSQL connection URI",
    )
    enable_store: bool = Field(
        default=False,
        description="Also create an AsyncPostgresStore for long-term memory",
    )


AnyMemoryConfig = Union[InMemoryConfig, PostgresConfig]


@asynccontextmanager
async def create_checkpointer(
    config: AnyMemoryConfig | None = None,
) -> AsyncIterator[Union[InMemorySaver, AsyncPostgresSaver]]:
    """Create and yield a checkpointer for the given memory config."""
    if config is None or config.kind == MemoryKind.INMEMORY:
        yield InMemorySaver()
        return

    if config.kind == MemoryKind.POSTGRES:
        assert isinstance(config, PostgresConfig)
        async with AsyncPostgresSaver.from_conn_string(
            config.connection_string,
        ) as checkpointer:
            await checkpointer.setup()
            yield checkpointer
        return

    raise ValueError(f"Unknown memory kind: {config.kind}")


@asynccontextmanager
async def create_store(
    config: PostgresConfig | None = None,
) -> AsyncIterator[BaseStore | None]:
    """Create and yield a long-term memory store."""
    if config is None or not config.enable_store or config.kind != MemoryKind.POSTGRES:
        yield None
        return

    from langgraph.store.postgres.aio import AsyncPostgresStore

    async with AsyncPostgresStore.from_conn_string(
        config.connection_string,
    ) as store:
        await store.setup()
        yield store
        return
