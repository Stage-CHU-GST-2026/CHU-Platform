"""Load agent configuration from agent.yaml."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from ai.models.config import AgentConfig


def load_agent_config(yaml_path: str | Path) -> AgentConfig:
    """Load an AgentConfig from an agent.yaml file.

    Args:
        yaml_path: Path to the agent.yaml file.

    Returns:
        AgentConfig with model settings from the YAML.
    """
    yaml_path = Path(yaml_path).expanduser().resolve()
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    return AgentConfig(
        model=data.get("model", "gpt-4o-mini"),
        temperature=data.get("temperature", 0.0),
        max_iterations=data.get("max_iterations", 15),
    )


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
