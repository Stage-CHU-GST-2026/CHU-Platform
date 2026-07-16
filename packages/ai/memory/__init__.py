"""Pluggable memory backends for AI agents.

Provides ``InMemory`` and ``Postgres`` memory configurations that can be
swapped without changing agent code.

Usage:
    # In-memory (default)
    from ai.memory import InMemoryConfig
    agent = Agent(config=cfg, memory=InMemoryConfig(), ...)

    # Postgres
    from ai.memory import PostgresConfig
    async with PostgresConfig().create_checkpointer() as checkpointer:
        agent = Agent(config=cfg, checkpointer=checkpointer, ...)
"""

from .config import InMemoryConfig, MemoryConfig, PostgresConfig
from .factory import create_checkpointer, create_store

__all__ = [
    "InMemoryConfig",
    "MemoryConfig",
    "PostgresConfig",
    "create_checkpointer",
    "create_store",
]
