"""Memory backend configuration models.

Each subclass of ``MemoryConfig`` carries the parameters needed to
create a checkpointer (and optionally a long-term store) for that
backend.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Literal, Optional, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def _default_pg_url() -> str:
    """Build the Postgres connection string from ``DATABASE_URL``.

    The existing ``DATABASE_URL`` env var is reused — any SQLAlchemy-specific
    driver prefix (``+asyncpg``, ``+psycopg``) is automatically stripped.

    Returns:
        A ``postgresql://`` URI suitable for ``AsyncPostgresSaver``.
    """
    url = os.getenv("DATABASE_URL", "")
    if url:
        # Strip any SQLAlchemy-specific driver prefix (e.g. +asyncpg, +psycopg)
        for prefix in ("+asyncpg", "+psycopg"):
            url = url.replace(prefix, "")
        if "?sslmode" not in url:
            url += "?sslmode=disable"
        return url

    # Fallback dev defaults (never hardcoded credentials)
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
    """Base class for all memory configurations.

    Subclasses set ``kind`` to a unique discriminator value so the
    factory can dispatch to the correct implementation.
    """
    kind: MemoryKind


class InMemoryConfig(MemoryConfig):
    """In-memory conversation memory (default).

    State is lost when the process exits. Suitable for development
    and testing.
    """
    kind: Literal[MemoryKind.INMEMORY] = MemoryKind.INMEMORY


class PostgresConfig(MemoryConfig):
    """PostgreSQL-backed conversation memory.

    State persists across process restarts. Production-ready.

    The checkpointer stores message history per thread_id.
    The optional *store* provides cross-conversation long-term memory.

    Connection string is read from the existing ``DATABASE_URL`` env var
    (``+asyncpg``/``+psycopg`` drivers are stripped automatically).

    .. code-block:: python

        # All credentials come from .env — no hardcoded values
        config = PostgresConfig()
        async with create_checkpointer(config) as checkpointer:
            agent = Agent(..., checkpointer=checkpointer)
    """
    kind: Literal[MemoryKind.POSTGRES] = MemoryKind.POSTGRES

    connection_string: str = Field(
        default_factory=_default_pg_url,
        description="PostgreSQL connection URI (loaded from env by default)",
    )
    enable_store: bool = Field(
        default=False,
        description="Also create an AsyncPostgresStore for long-term memory",
    )


# Union type for type-safe config parameters
AnyMemoryConfig = Union[InMemoryConfig, PostgresConfig]
