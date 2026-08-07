"""Load agent configuration from agent.yaml with env var overrides."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

import yaml

load_dotenv()


class DataAnalystConfig(BaseModel):
    """Configuration for the Data Analyst agent.

    All values can be overridden via environment variables:
      AGENT_MODEL, AGENT_TEMPERATURE, AGENT_MAX_ITERATIONS,
      OPENAI_BASE_URL, OPENAI_API_KEY
    """

    model: str = Field(
        default_factory=lambda: os.getenv(
            "AGENT_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"
        )
    )
    base_url: str = Field(
        default_factory=lambda: os.getenv("OPENAI_BASE_URL", "http://localhost:6060/v1")
    )
    api_key: str = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("AGENT_TEMPERATURE", "0.0"))
    )
    max_tokens: int | None = Field(default=None)
    max_iterations: int = Field(
        default_factory=lambda: int(os.getenv("AGENT_MAX_ITERATIONS", "15"))
    )
    recursion_limit: int = Field(default=100)


# Backward compatibility alias
AgentConfig = DataAnalystConfig


def load_agent_config(yaml_path: str | Path) -> DataAnalystConfig:
    """Load a DataAnalystConfig from an agent.yaml file."""
    yaml_path = Path(yaml_path).expanduser().resolve()
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    kwargs: dict = {}

    if "AGENT_MODEL" not in os.environ:
        kwargs["model"] = data.get("model", "gpt-4o-mini")
    if "AGENT_TEMPERATURE" not in os.environ:
        kwargs["temperature"] = data.get("temperature", 0.0)
    if "AGENT_MAX_ITERATIONS" not in os.environ:
        kwargs["max_iterations"] = data.get("max_iterations", 15)

    return DataAnalystConfig(**kwargs)


def load_prompt(prompt_path: str | Path) -> str:
    """Load the system prompt from a markdown file."""
    prompt_path = Path(prompt_path).expanduser().resolve()
    with open(prompt_path) as f:
        return f.read().strip()


_HERE = Path(__file__).parent
DEFAULT_YAML = _HERE / "agent.yaml"
DEFAULT_PROMPT = _HERE / "prompt.md"
