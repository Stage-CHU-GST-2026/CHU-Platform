"""Generic agent configuration."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class AgentConfig(BaseModel):
    """Configuration for the generic AI Agent."""

    model: str = Field(default="gpt-4o-mini")
    base_url: str = Field(default=os.getenv(
        "OPENAI_BASE_URL", "http://localhost:6060/v1"))
    api_key: str = Field(default=os.getenv("OPENAI_API_KEY", ""))
    temperature: float = Field(default=0.0)
    max_tokens: int | None = Field(default=None)
    max_iterations: int = Field(default=15)
    recursion_limit: int = Field(default=100)
