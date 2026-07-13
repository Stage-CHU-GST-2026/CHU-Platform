"""Wraps the Data Analyst agent and handles prompt construction."""

from __future__ import annotations

from langchain_core.messages import AIMessageChunk, ToolMessage

from agents.data_analyst import create_data_analyst
from ai import Agent
from tools.visualization.visualization import CHART_URL_PREFIX


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
        """Stream agent tokens and chart URLs for a given message and thread.

        Yields either:
          ("token", text)   — a text token to append to the assistant message
          ("image", url)    — a chart URL to render inline
        """
        prompt = self.build_prompt(message, dataset_path)
        async for chunk, _metadata in self._agent.graph.astream(
            {"messages": [{"role": "user", "content": prompt}]},
            stream_mode="messages",
            config={"configurable": {"thread_id": thread_id}},
        ):
            # Text tokens from the LLM
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield ("token", chunk.content)

            # Tool results — inspect for chart URLs
            elif isinstance(chunk, ToolMessage) and chunk.content:
                content = str(chunk.content)
                for line in content.splitlines():
                    if line.startswith(CHART_URL_PREFIX):
                        url = line[len(CHART_URL_PREFIX):]
                        yield ("image", url)
