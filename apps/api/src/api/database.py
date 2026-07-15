"""Async SQLAlchemy engine, session factory, and declarative base.

Usage:
    from api.database import AsyncSessionLocal, engine, Base
    from api.config import settings
    from sqlalchemy import select
    from api.models.conversation import Conversation

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Conversation))
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from api.config import settings

# ── Async engine ──────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=False,                          # set to True for SQL logging
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# ── Session factory ───────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Declarative base ──────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ── Dependency for FastAPI ────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    The session is automatically closed when the request finishes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
