"""Data Analyst agent — almost empty.

Its only job is to configure the generic AI framework with:
- A prompt (personality)
- A tool list (capabilities)
- Model settings (from agent.yaml)
- A pluggable memory backend
"""

from __future__ import annotations

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.base import BaseStore

from ai import Agent
from ai.models.config import AgentConfig

from .config import DEFAULT_PROMPT, DEFAULT_YAML, load_agent_config, load_prompt
from .tools import DATA_ANALYST_TOOLS


def create_data_analyst(
    config: AgentConfig | None = None,
    checkpointer: InMemorySaver | None = None,
    store: BaseStore | None = None,
) -> Agent:
    """Create a Data Analyst agent from configuration.

    Args:
        config: Optional override config. If None, loads from agent.yaml.
        checkpointer: Optional memory backend. If None, uses InMemorySaver.
                      Pass a PostgresSaver for persistent memory.
        store: Optional long-term memory store (e.g. PostgresStore).

    Returns:
        A configured Agent instance.
    """
    cfg = config or load_agent_config(DEFAULT_YAML)
    prompt = load_prompt(DEFAULT_PROMPT)

    return Agent(
        config=cfg,
        tools=DATA_ANALYST_TOOLS,
        prompt=prompt,
        checkpointer=checkpointer,
        store=store,
    )
