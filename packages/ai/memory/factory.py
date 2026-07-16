"""Factory functions for creating memory backends.

Usage:

    from ai.memory import InMemoryConfig, PostgresConfig, create_checkpointer

    # Simple sync — in-memory (default)
    checkpointer = create_checkpointer(InMemoryConfig())

    # Async context manager — Postgres
    async with create_checkpointer(PostgresConfig()) as checkpointer:
        agent = Agent(..., checkpointer=checkpointer)
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Union

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.base import BaseStore

from .config import (
    AnyMemoryConfig,
    InMemoryConfig,
    MemoryKind,
    PostgresConfig,
)


@asynccontextmanager
async def create_checkpointer(
    config: AnyMemoryConfig | None = None,
) -> AsyncIterator[Union[InMemorySaver, AsyncPostgresSaver]]:
    """Create and yield a checkpointer for the given memory config.

    For **InMemory** — yields immediately with no setup.

    For **Postgres** — opens an async connection, runs ``setup()``
    on first use, and closes the connection on exit.

    Args:
        config: Memory configuration.  ``None`` defaults to
                ``InMemoryConfig()``.

    Yields:
        A configured checkpointer, ready to pass to
        ``Agent(..., checkpointer=...)``.
    """
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
    """Create and yield a long-term memory store.

    Currently only supports Postgres.  Returns ``None`` if the config
    does not enable a store.

    Args:
        config: Postgres memory config with ``enable_store=True``.

    Yields:
        A ``BaseStore`` instance, or ``None``.
    """
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
