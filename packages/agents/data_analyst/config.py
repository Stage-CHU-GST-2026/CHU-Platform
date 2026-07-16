"""Load agent configuration from agent.yaml with env var overrides."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from ai.models.config import AgentConfig


def load_agent_config(yaml_path: str | Path) -> AgentConfig:
    """Load an AgentConfig from an agent.yaml file.

    Environment variables take priority over YAML values:
      AGENT_MODEL, AGENT_TEMPERATURE, AGENT_MAX_ITERATIONS,
      OPENAI_BASE_URL, OPENAI_API_KEY

    Args:
        yaml_path: Path to the agent.yaml file.

    Returns:
        AgentConfig with model settings from the YAML, overridden by env.
    """
    yaml_path = Path(yaml_path).expanduser().resolve()
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    kwargs: dict = {}

    # Only pull from yaml if the corresponding env var is NOT set
    if "AGENT_MODEL" not in os.environ:
        kwargs["model"] = data.get("model", "gpt-4o-mini")
    if "AGENT_TEMPERATURE" not in os.environ:
        kwargs["temperature"] = data.get("temperature", 0.0)
    if "AGENT_MAX_ITERATIONS" not in os.environ:
        kwargs["max_iterations"] = data.get("max_iterations", 15)

    return AgentConfig(**kwargs)


def load_prompt(prompt_path: str | Path) -> str:
    """Load the system prompt from a markdown file.

    Args:
        prompt_path: Path to the prompt.md file.

    Returns:
        Prompt text.
    """
    prompt_path = Path(prompt_path).expanduser().resolve()
    with open(prompt_path) as f:
        return f.read().strip()


# Default config paths relative to this file
_HERE = Path(__file__).parent
DEFAULT_YAML = _HERE / "agent.yaml"
DEFAULT_PROMPT = _HERE / "prompt.md"
