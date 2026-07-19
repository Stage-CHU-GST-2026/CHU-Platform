"""Wraps the Data Analyst agent and handles prompt construction."""

from __future__ import annotations

from langchain_core.messages import AIMessageChunk, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.base import BaseStore

from agents.data_analyst import create_data_analyst
from ai import Agent
from tools.visualization.visualization import CHART_URL_PREFIX
from tools.planning import ARTIFACT_URL_PREFIX


class AgentService:
    """Thin wrapper around the Data Analyst agent.

    Accepts a pluggable checkpointer so memory backends can be
    swapped (InMemory ↔ Postgres) without changing the service code.
    """

    def __init__(
        self,
        checkpointer: InMemorySaver | None = None,
        store: BaseStore | None = None,
    ) -> None:
        self._agent: Agent = create_data_analyst(
            checkpointer=checkpointer,
            store=store,
        )

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
          ("token", text)      — a text token to append to the assistant message
          ("image", url)       — a chart URL to render inline
          ("artifact", json)   — plan artifact metadata JSON
        """
        prompt = self.build_prompt(message, dataset_path)
        async for chunk, metadata in self._agent.graph.astream(
            {"messages": [{"role": "user", "content": prompt}], "summary": ""},
            stream_mode="messages",
            config={"configurable": {"thread_id": thread_id}},
        ):
            # Text tokens from the LLM — only yield from the "agent" node
            # to avoid leaking the "summarize" node's output into the stream.
            if (
                isinstance(chunk, AIMessageChunk)
                and chunk.content
                and metadata.get("langgraph_node") == "agent"
            ):
                yield ("token", chunk.content)

            # Tool results — inspect for chart URLs and artifact URLs
            elif isinstance(chunk, ToolMessage) and chunk.content:
                content = str(chunk.content)
                for line in content.splitlines():
                    if line.startswith(CHART_URL_PREFIX):
                        url = line[len(CHART_URL_PREFIX):]
                        yield ("image", url)
                    elif line.startswith(ARTIFACT_URL_PREFIX):
                        metadata = line[len(ARTIFACT_URL_PREFIX):]
                        yield ("artifact", metadata)
