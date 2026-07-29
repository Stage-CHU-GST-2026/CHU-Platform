"""Wraps the Data Analyst agent and handles prompt construction.

Supports two streaming modes:
- **Orchestrated** (default): Plan → Execute steps → Synthesize.
  Streams plan, step_started, step_update, step_finished, token,
  image, artifact, and done events.
- **Legacy** (fast path for simple queries): Direct LLM streaming
  with token, image, artifact, and done events.
"""

from __future__ import annotations

from typing import AsyncGenerator

import json

from langchain_core.messages import AIMessageChunk, ToolMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.store.base import BaseStore

from agents.data_analyst import create_data_analyst, Orchestrator
from ai import Agent
from analysis.charts import ChartArtifact
from tools.visualization.visualization import CHART_ARTIFACT_PREFIX, CHART_URL_PREFIX
from tools.planning import ARTIFACT_URL_PREFIX
from tools.inspection.describe import register_datasets


class AgentService:
    """Wrapper around the Data Analyst agent with orchestrator support.

    Accepts a pluggable checkpointer so memory backends can be
    swapped (InMemory ↔ Postgres) without changing the service code.

    For complex analytical queries, uses the Orchestrator to plan,
    execute step-by-step, and synthesize findings. For simple
    questions, falls back to direct LLM streaming.
    """

    def __init__(
        self,
        checkpointer: BaseCheckpointSaver | None = None,
        store: BaseStore | None = None,
    ) -> None:
        self._agent: Agent = create_data_analyst(
            checkpointer=checkpointer,
            store=store,
        )
        self._orchestrator = Orchestrator(self._agent, self._agent.config)

    @property
    def agent(self) -> Agent:
        return self._agent

    @staticmethod
    def register_db_datasets(datasets: list[dict]) -> None:
        """Populate the agent's dataset registry from database records.

        Called once at startup so the ``list_datasets`` tool returns
        DB-backed datasets instead of scanning the filesystem.
        """
        register_datasets(datasets)

    def build_prompt(self, message: str, dataset_path: str | None = None) -> str:
        """Prepend dataset context to the user message if provided."""
        if dataset_path and dataset_path not in message:
            return (
                f"[Dataset: {dataset_path}]\n"
                f"The dataset above is already linked to this conversation. "
                f"Do NOT call list_datasets — use the provided path directly "
                f"with analysis tools.\n\n"
                f"{message}"
            )
        return message

    async def stream(
        self,
        message: str,
        thread_id: str,
        dataset_path: str | None = None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        """Stream agent events for a given message and thread.

        Uses the orchestrator for complex queries (plan → execute →
        synthesize) with step-level progress events. Falls back to
        direct LLM streaming for simple questions.

        Yields:
            ("plan", json)           — execution plan (list of steps)
            ("step_started", json)   — {id, title, description, tool_hint}
            ("step_update", str)     — progress message within a step
            ("step_finished", json)  — {id}
            ("token", str)           — text token (final synthesis)
            ("image", str)           — chart URL to render inline
            ("artifact", json)       — plan artifact metadata JSON
            ("done", str)            — stream complete
        """
        prompt = self.build_prompt(message, dataset_path)

        # Use the orchestrator for the full plan→execute→synthesize flow
        async for event_type, data in self._orchestrator.stream(
            message=prompt,
            thread_id=thread_id,
            dataset_path=dataset_path,
        ):
            yield (event_type, data)

    async def stream_legacy(
        self,
        message: str,
        thread_id: str,
        dataset_path: str | None = None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        """Legacy streaming mode — direct LLM tokens without planning.

        Useful as a fallback or for simple conversational turns.
        """
        prompt = self.build_prompt(message, dataset_path)
        async for chunk, metadata in self._agent.graph.astream(
            {"messages": [{"role": "user", "content": prompt}], "summary": ""},
            stream_mode="messages",
            config={"configurable": {"thread_id": thread_id}},
        ):
            if (
                isinstance(chunk, AIMessageChunk)
                and chunk.content
                and metadata.get("langgraph_node") == "agent"
            ):
                yield ("token", chunk.content)
            elif isinstance(chunk, ToolMessage) and chunk.content:
                content = str(chunk.content)
                for line in content.splitlines():
                    if line.startswith(CHART_ARTIFACT_PREFIX):
                        raw_json = line[len(CHART_ARTIFACT_PREFIX):]
                        try:
                            artifact = ChartArtifact.from_dict(
                                json.loads(raw_json))
                            yield ("image", artifact.api_url)
                            yield ("chart_artifact", artifact.to_dict())
                        except Exception:
                            pass
                    elif line.startswith(CHART_URL_PREFIX):
                        yield ("image", line[len(CHART_URL_PREFIX):])
                    elif line.startswith(ARTIFACT_URL_PREFIX):
                        yield ("artifact", line[len(ARTIFACT_URL_PREFIX):])
