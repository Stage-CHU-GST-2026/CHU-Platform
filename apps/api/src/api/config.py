"""API configuration loaded from environment."""

from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str:
    """Locate the root .env file regardless of the current working directory."""
    # Resolve relative to THIS file: config.py → project root
    _here = os.path.dirname(os.path.abspath(__file__))  # .../src/api
    _candidates = [
        os.path.join(_here, "..", "..", "..", "..",
                     ".env"),  # via config.py path
        os.path.join(os.getcwd(), ".env"),                    # CWD fallback
    ]
    for p in _candidates:
        resolved = os.path.abspath(p)
        if os.path.isfile(resolved):
            return resolved
    # Fallback — let pydantic-settings try the default
    return "../../.env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 10000
    reload: bool = True

    # Database (PostgreSQL)
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/app"
    )

    # Charts — directory inside the API package, served as static files
    charts_dir: str = "static/charts"

    # LLM — matches what the Data Analyst agent picks up
    openai_base_url: str = "http://localhost:6060/v1"
    openai_api_key: str = ""

    # Agent
    agent_max_iterations: int = 15
    agent_temperature: float = 0.0
    agent_model: str = "gpt-4o-mini"


settings = Settings()
