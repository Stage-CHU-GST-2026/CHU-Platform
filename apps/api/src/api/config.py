"""API configuration loaded from environment."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../../.env",
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
