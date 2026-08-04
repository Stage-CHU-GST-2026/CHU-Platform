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
from api.services.dataset_service import resolve_dataset_path


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
        Stored filepaths are resolved so host-absolute DB records still
        work when the API runs inside a container.
        """
        resolved: list[dict] = []
        for d in datasets:
            item = dict(d)
            if item.get("filepath"):
                item["filepath"] = str(resolve_dataset_path(item["filepath"]))
            resolved.append(item)
        register_datasets(resolved)

    def build_prompt(
        self,
        message: str,
        dataset_path: str | None = None,
        dataset_info: dict | None = None,
        is_first_turn: bool = True,
    ) -> str:
        """Prepend dataset context. Full profiling is sent ONLY on the first turn of a conversation; subsequent turns use minimal dataset path header to conserve tokens."""
        if not dataset_path and dataset_info:
            dataset_path = dataset_info.get("filepath")

        if not dataset_path and not dataset_info:
            return message

        if dataset_path and f"[Dataset: {dataset_path}]" in message:
            return message

        # On subsequent turns (is_first_turn=False), conversation memory already contains full context.
        # Send only the minimal dataset tag header to save tokens.
        if not is_first_turn:
            return f"[Dataset: {dataset_path}]\n\n{message}"

        context_blocks = [f"[Dataset: {dataset_path}]"]
        context_blocks.append(
            "The dataset above is linked to this conversation. ALL DATASET CONTEXT, PHYSICAL SCHEMA PROFILING, NUMERIC STATISTICS, AND SEMANTIC MAPPINGS ARE PRE-COMPUTED AND PROVIDED BELOW:"
        )

        if dataset_info:
            if dataset_info.get("filename"):
                context_blocks.append(
                    f"- Original Filename: {dataset_info['filename']}")
            if dataset_info.get("rows") is not None and dataset_info.get("columns") is not None:
                context_blocks.append(
                    f"- Dataset Shape: {dataset_info['rows']:,} rows × {dataset_info['columns']} columns"
                )
            if dataset_info.get("context_description"):
                context_blocks.append(
                    f"- Business Overview: {dataset_info['context_description']}")
            if dataset_info.get("context_notes"):
                context_blocks.append(
                    f"- Business Rules & Notes: {dataset_info['context_notes']}")

            cols_info = dataset_info.get("columns_info")
            if cols_info:
                context_blocks.append(
                    "\n### Pre-computed Physical Schema Profiling:")
                context_blocks.append(
                    f"{'Column Name':<25} {'Data Type':<12} {'Null Count':<12} {'Null %':<8} {'Unique':<8} {'Sample'}"
                )
                context_blocks.append("-" * 80)
                tot_rows = dataset_info.get("rows") or 1
                for c in cols_info:
                    cn = str(c.get("name", ""))
                    dt = str(c.get("dtype", ""))
                    nc = c.get("null_count", 0)
                    npct = f"{round((nc / tot_rows) * 100)}%"
                    uc = c.get("unique_count", 0)
                    samp = str(c.get("sample") or "—")[:25]
                    context_blocks.append(
                        f"{cn:<25} {dt:<12} {nc:<12} {npct:<8} {uc:<8} {samp}"
                    )

            stats = dataset_info.get("statistics")
            if stats and isinstance(stats, dict):
                num_summary = stats.get("numeric_summary")
                if num_summary and isinstance(num_summary, dict):
                    context_blocks.append(
                        "\n### Pre-computed Numeric Summary Matrix:")
                    context_blocks.append(
                        f"{'Metric':<10} " +
                        " ".join([f"{col:<15}" for col in num_summary.keys()])
                    )
                    context_blocks.append("-" * 75)
                    for metric in ["count", "mean", "std", "min", "50%", "max"]:
                        row_vals = []
                        for col, col_stats in num_summary.items():
                            val = col_stats.get(metric)
                            if isinstance(val, (int, float)):
                                row_vals.append(f"{val:<15.4g}")
                            else:
                                row_vals.append(f"{'—':<15}")
                        context_blocks.append(
                            f"{metric:<10} " + " ".join(row_vals))

            semantics = dataset_info.get("semantic_mappings")
            if semantics and isinstance(semantics, list):
                context_blocks.append(
                    "\n### Pre-computed Semantic Concept Mappings & Business Glossary:")
                context_blocks.append(
                    f"{'Raw Column':<25} {'DataType':<10} {'Mapped Concept':<30} {'Category':<15} {'Confidence'}"
                )
                context_blocks.append("-" * 90)
                for m in semantics:
                    r_col = str(m.get("column_name", ""))
                    r_dt = str(m.get("dtype", ""))
                    r_conc = str(m.get("mapped_concept", ""))
                    r_cat = str(m.get("category", ""))
                    r_conf = f"{m.get('confidence', 0)}%"
                    context_blocks.append(
                        f"{r_col:<25} {r_dt:<10} {r_conc:<30} {r_cat:<15} {r_conf}"
                    )

        context_blocks.append(
            "\nCRITICAL INSTRUCTION FOR TOOL CALLING & PLANNING:")
        context_blocks.append(
            "- All schema profiling, basic statistics, column types, and semantic mappings are ALREADY PRE-COMPUTED and provided above."
        )
        context_blocks.append(
            "- Do NOT call inspection/profiling tools (`describe_dataset`, `dataset_summary`, `list_columns`, `column_info`, `dataset_shape`, or `list_datasets`) to re-calculate basic statistics or schema information."
        )
        context_blocks.append(
            "- Use the pre-computed dataset context directly for your analysis and reasoning."
        )

        formatted_context = "\n".join(context_blocks)
        return f"{formatted_context}\n\n{message}"

    async def stream(
        self,
        message: str,
        thread_id: str,
        dataset_path: str | None = None,
        dataset_info: dict | None = None,
        is_first_turn: bool = True,
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
        prompt = self.build_prompt(
            message, dataset_path, dataset_info, is_first_turn)

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
        dataset_info: dict | None = None,
        is_first_turn: bool = True,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        """Legacy streaming mode — direct LLM tokens without planning.

        Useful as a fallback or for simple conversational turns.
        """
        prompt = self.build_prompt(
            message, dataset_path, dataset_info, is_first_turn)
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
