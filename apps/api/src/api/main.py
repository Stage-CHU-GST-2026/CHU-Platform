"""FastAPI application factory."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.config import settings
from api.database import Base, engine
from api.routers.chat import router as chat_router
from api.routers.conversations import router as conversations_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup / shutdown lifecycle.

    On startup: create DB tables, ensure the charts directory exists
    and tell the visualization tool where to save plots.
    On shutdown: dispose of the database connection pool.
    """
    # Resolve charts directory inside the API package & create it
    abs_charts_dir = _charts_abs_dir()
    os.makedirs(abs_charts_dir, exist_ok=True)

    # Override the tool's hardcoded /tmp path so charts persist
    import tools.visualization.visualization as viz_mod
    viz_mod.CHARTS_DIR = abs_charts_dir

    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: dispose engine
    await engine.dispose()


def _charts_abs_dir() -> str:
    """Resolve charts_dir relative to the API package root."""
    _api_root = os.path.dirname(os.path.abspath(__file__))  # .../src/api
    return os.path.abspath(
        os.path.join(_api_root, "..", "..", settings.charts_dir)
    )


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

    # ----- Static files: generated charts -----
    # Mount AFTER routers so API routes take precedence.
    charts_static = StaticFiles(directory=_charts_abs_dir())
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
