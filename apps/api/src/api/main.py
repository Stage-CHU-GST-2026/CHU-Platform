"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.config import settings
from api.routers.chat import router as chat_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Data Analyst API",
        version="0.1.0",
        description="Backend for the Data Analyst agent. "
        "Streams LLM responses via SSE.",
    )

    # ----- Routers -----
    app.include_router(chat_router, prefix="/api/v1")

    # ----- Static files: generated charts -----
    # Must be mounted AFTER including the router so /api/v1/chat routes
    # take precedence over the static mount.
    from api.routers.chat import charts_static  # noqa: PLC0415
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
