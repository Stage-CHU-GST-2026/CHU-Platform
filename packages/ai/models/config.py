"""Generic agent configuration."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class AgentConfig(BaseModel):
    """Configuration for the generic AI Agent.

    All values can be overridden via environment variables:
      AGENT_MODEL, AGENT_TEMPERATURE, AGENT_MAX_ITERATIONS,
      OPENAI_BASE_URL, OPENAI_API_KEY
    """

    model: str = Field(
        default=os.getenv("AGENT_MODEL",
                          "meta-llama/llama-4-scout-17b-16e-instruct")
    )
    base_url: str = Field(
        default=os.getenv("OPENAI_BASE_URL", "http://localhost:6060/v1")
    )
    api_key: str = Field(default=os.getenv("OPENAI_API_KEY", ""))
    temperature: float = Field(
        default=float(os.getenv("AGENT_TEMPERATURE", "0.0"))
    )
    max_tokens: int | None = Field(default=None)
    max_iterations: int = Field(
        default=int(os.getenv("AGENT_MAX_ITERATIONS", "15"))
    )
    recursion_limit: int = Field(default=100)
