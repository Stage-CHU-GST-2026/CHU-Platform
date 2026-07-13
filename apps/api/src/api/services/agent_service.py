"""Wraps the Data Analyst agent and handles prompt construction."""

from __future__ import annotations

from agents.data_analyst import create_data_analyst
from ai import Agent


class AgentService:
    """Thin wrapper around the Data Analyst agent."""

    def __init__(self) -> None:
        self._agent: Agent = create_data_analyst()

    @property
    def agent(self) -> Agent:
        return self._agent

    def build_prompt(self, message: str, dataset_path: str | None = None) -> str:
        """Prepend dataset context to the user message if provided."""
        if dataset_path and dataset_path not in message:
            return f"[Dataset: {dataset_path}]\n{message}"
        return message

    async def stream(self, message: str, thread_id: str, dataset_path: str | None = None):
        """Stream agent tokens for a given message and thread."""
        prompt = self.build_prompt(message, dataset_path)
        async for token in self._agent.astream(
            prompt,
            config={"configurable": {"thread_id": thread_id}},
        ):
            yield token
