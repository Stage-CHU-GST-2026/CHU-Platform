"""FastAPI application factory."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.config import settings, get_charts_abs_dir
from api.database import Base, engine
from api.routers.artifacts import router as artifacts_router
from api.routers.chat import router as chat_router
from api.routers.conversations import router as conversations_router
from api.services.session import session_manager


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup / shutdown lifecycle.

    On startup: create DB tables, ensure the charts directory exists,
    tell the visualization tool where to save plots, and initialise
    the agent's Postgres-backed checkpointer.

    On shutdown: dispose of the database connection pool and close
    the checkpointer connection.
    """
    # Resolve charts directory inside the API package & create it
    abs_charts_dir = get_charts_abs_dir()
    os.makedirs(abs_charts_dir, exist_ok=True)

    # Override the tool's hardcoded /tmp path so charts persist
    import tools.visualization.visualization as viz_mod
    viz_mod.CHARTS_DIR = abs_charts_dir

    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # ── Agent memory: Postgres checkpointer ──────────────────────
    from ai.memory import PostgresConfig
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
    from psycopg import AsyncConnection

    pg_config = PostgresConfig()  # reads DATABASE_URL from .env
    pg_conn = await AsyncConnection.connect(pg_config.connection_string)
    pg_checkpointer = AsyncPostgresSaver(pg_conn)
    await pg_checkpointer.setup()

    session_manager.set_checkpointer(pg_checkpointer)

    yield

    # Shutdown
    await pg_conn.close()
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Data Analyst API",
        version="0.1.0",
        description="Backend for the Data Analyst agent. "
        "Streams LLM responses via SSE.",
        lifespan=lifespan,
    )

    # ----- Routers -----
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(conversations_router, prefix="/api/v1")
    app.include_router(artifacts_router, prefix="/api/v1")

    # ----- Static files: generated charts -----
    # Mount AFTER routers so API routes take precedence.
    charts_static = StaticFiles(directory=get_charts_abs_dir())
    app.mount("/api/v1/charts", charts_static, name="charts")

    # ----- Global error handler -----
    @app.exception_handler(Exception)
    async def global_exception(_request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal error: {exc}"},
        )

    # ----- Health -----
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
