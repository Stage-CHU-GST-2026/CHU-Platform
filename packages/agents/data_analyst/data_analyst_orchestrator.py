"""Orchestrator — manages the plan → execute → synthesize workflow via LangGraph.

Coordinates the Planner, the Data Analyst Agent (for tool execution),
and the final synthesis LLM call with built-in fault tolerance, step retries,
and memory checkpointer integration.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from pathlib import Path
from typing import AsyncGenerator, Literal

from langchain_core.callbacks import adispatch_custom_event
from langchain_core.messages import AIMessageChunk, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from .agent import DataAnalystAgent as Agent
from .config import DataAnalystConfig as AgentConfig
from .data_analyst_planner import ExecutionPlan, PlanStep, generate_plan
from .graph import build_data_analyst_graph
from .logger import get_logger
from .state import DataAnalystState as AgentState
from analysis.charts import ChartArtifact
from tools import ARTIFACT_URL_PREFIX, CHART_ARTIFACT_PREFIX, CHART_URL_PREFIX

logger = get_logger(__name__)

# ── Prompts ────────────────────────────────────────────────────────────

_PROMPTS_DIR = Path(__file__).parent / "prompts"

with open(_PROMPTS_DIR / "step_prompt.md") as f:
    STEP_SYSTEM_PROMPT = f.read()

with open(_PROMPTS_DIR / "synthesis_prompt.md") as f:
    SYNTHESIS_SYSTEM_PROMPT = f.read()

# ── Orchestrator ───────────────────────────────────────────────────────


class Orchestrator:
    """Coordinates the plan → execute → synthesize workflow via a LangGraph state machine.

    Includes automatic step retries, self-correction, state reducers, and
    checkpointer memory persistence.
    """

    def __init__(self, agent: Agent, config: AgentConfig) -> None:
        self._agent = agent
        self._config = config

        # Build the fault-tolerant orchestrator graph
        workflow = StateGraph(AgentState)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("step_error_recovery", self._step_error_recovery_node)
        workflow.add_node("synthesizer", self._synthesizer_node)

        workflow.add_edge(START, "planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("step_error_recovery", "executor")

        workflow.add_conditional_edges(
            "executor",
            self._route_execution,
            {
                "executor": "executor",
                "step_error_recovery": "step_error_recovery",
                "synthesizer": "synthesizer",
            },
        )
        workflow.add_edge("synthesizer", END)

        # Compile with checkpointer for state persistence
        self._graph = workflow.compile(checkpointer=self._agent.checkpointer)

        # ── Synthesis graph: same model, NO tools, shared memory checkpointer ──
        self._synthesis_graph = build_data_analyst_graph(
            config=config,
            tools=[],  # empty — no tool calling during synthesis
            prompt=SYNTHESIS_SYSTEM_PROMPT,
            checkpointer=self._agent.checkpointer,
        )

    async def _emit(self, event_type: str, data: str | dict):
        """Helper to dispatch custom events to be caught by stream()."""
        await adispatch_custom_event(
            "orchestrator_event", {"type": event_type, "data": data}
        )

    async def _planner_node(self, state: AgentState, config: RunnableConfig) -> dict:
        logger.info("Phase 1: Generating plan")
        original_message = state.get("original_message", "")
        dataset_path = state.get("dataset_path")

        try:
            plan = await generate_plan(original_message, self._config, dataset_path)
        except Exception as e:
            logger.error("Plan generation failed, using fallback", error=str(e))
            plan = self._fallback_plan()

        await self._emit("plan", json.dumps(plan.to_dict()))

        run_id = uuid.uuid4().hex[:8]

        return {
            "plan": plan.to_dict(),
            "current_step": 0,
            "evidence": "",
            "generated_charts": [],
            "run_id": run_id,
            "step_retries": 0,
            "max_retries": 2,
            "last_step_error": None,
            "status": "executing",
        }

    async def _executor_node(self, state: AgentState, config: RunnableConfig) -> dict:
        plan_dict = state.get("plan", {})
        plan = ExecutionPlan.from_dict(plan_dict)
        current_step_idx = state.get("current_step", 0)

        if current_step_idx >= len(plan.steps):
            return {}

        step = plan.steps[current_step_idx]
        run_id = state.get("run_id", "default_run")
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        original_message = state.get("original_message", "")
        dataset_path = state.get("dataset_path")
        last_error = state.get("last_step_error")
        step_retries = state.get("step_retries", 0)

        logger.info(
            "Phase 2: Executing step",
            step_id=step.id,
            title=step.title,
            retry=step_retries,
        )
        await self._emit("step_started", json.dumps(step.to_dict()))

        if step.tool_hint == "synthesis":
            await self._emit("step_update", "Compiling final report...")
            await self._emit("step_finished", json.dumps({"id": step.id}))
            return {
                "current_step": current_step_idx + 1,
                "step_retries": 0,
                "last_step_error": None,
            }

        # Build step-specific instruction
        user_context = (
            f"## User's Original Request\n{original_message}\n\n"
            if original_message.strip()
            else ""
        )
        step_instruction = (
            f"{user_context}"
            f"## Current Step: {step.title}\n"
            f"{step.description}\n\n"
            f"Focus ONLY on this step and ONLY on the dataset(s) mentioned in the "
            f"user's request above. Do not inspect or analyse any other datasets. "
            f"Use tools to gather the needed information and report your findings "
            f"concisely when done."
        )

        if getattr(step, "needs_visualization", False):
            rationale = (
                getattr(step, "visualization_rationale", "")
                or "A chart would clarify the findings."
            )
            step_instruction += (
                f"\n\n## Visualization Required\n"
                f"{rationale}\n"
                f"After computing the statistics, generate the appropriate chart.\n"
                f"Follow the chart lifecycle:\n"
                f"1. Compute the data first.\n"
                f"2. Form a 1-2 sentence insight.\n"
                f"3. Call generate_chart with that insight in the `insight` parameter.\n"
                f"4. Reference the chart by title in your narrative."
            )

        if last_error:
            step_instruction += (
                f"\n\n## Self-Correction Feedback (Attempt {step_retries + 1})\n"
                f"Your previous attempt encountered an issue:\n"
                f"```\n{last_error}\n```\n"
                f"Please fix the error and try alternative arguments or tools."
            )

        if dataset_path:
            step_instruction = f"[Dataset: {dataset_path}]\n{step_instruction}"

        await self._emit("step_update", f"{step.title}...")

        evidence_tokens: list[str] = []
        buffered_artifacts: list[ChartArtifact] = []
        buffered_plan_artifacts: list[str] = []
        pending_by_id: dict[str, dict] = {}
        pending_by_index: dict[int, dict] = {}

        step_config = {
            "configurable": {
                "thread_id": f"{thread_id}_run_{run_id}_step_{step.id}_try_{step_retries}"
            }
        }

        try:
            async for chunk, metadata in self._agent.graph.astream(
                {
                    "messages": [HumanMessage(content=step_instruction)],
                    "summary": "",
                },
                stream_mode="messages",
                config=step_config,
            ):
                self._track_tool_call_chunk(chunk, pending_by_id, pending_by_index)

                if (
                    isinstance(chunk, AIMessageChunk)
                    and chunk.content
                    and metadata.get("langgraph_node") == "agent"
                ):
                    evidence_tokens.append(chunk.content)
                    await self._emit("step_token", chunk.content)

                elif isinstance(chunk, ToolMessage) and chunk.content:
                    tool_name, parameters, tc_id, duration_ms = (
                        self._extract_tool_evidence_params(
                            chunk, pending_by_id, pending_by_index
                        )
                    )
                    raw_result = str(chunk.content)

                    evidence_payload = {
                        "step_id": step.id,
                        "tool_name": tool_name,
                        "tool_call_id": tc_id,
                        "parameters": parameters,
                        "result": raw_result,
                        "status": getattr(chunk, "status", "success"),
                        "execution_time_ms": duration_ms,
                    }
                    await self._emit("tool_evidence", json.dumps(evidence_payload))

                    content = str(chunk.content)
                    for line in content.splitlines():
                        if line.startswith(CHART_ARTIFACT_PREFIX):
                            raw_json = line[len(CHART_ARTIFACT_PREFIX) :]
                            try:
                                artifact = ChartArtifact.from_dict(json.loads(raw_json))
                                buffered_artifacts.append(artifact)
                                await self._emit("image", artifact.api_url)
                                await self._emit("chart_artifact", artifact.to_dict())
                            except Exception as parse_err:
                                logger.warning(
                                    "Failed to parse ChartArtifact",
                                    error=str(parse_err),
                                    raw=raw_json[:200],
                                )
                        elif line.startswith(CHART_URL_PREFIX):
                            url = line[len(CHART_URL_PREFIX) :]
                            await self._emit("image", url)
                        elif line.startswith(ARTIFACT_URL_PREFIX):
                            buffered_plan_artifacts.append(
                                line[len(ARTIFACT_URL_PREFIX) :]
                            )

            full_evidence = "".join(evidence_tokens)
            for art in buffered_artifacts:
                full_evidence += f"\n\n{art.evidence_summary()}\n"
            for artifact_data in buffered_plan_artifacts:
                try:
                    meta = json.loads(artifact_data)
                    full_evidence += f"\n\n[Generated Artifact: {meta.get('filename')}]\n"
                except Exception:
                    pass

            if full_evidence.strip():
                step_evidence_str = (
                    f"\n## Step {step.id}: {step.title}\n{full_evidence.strip()}"
                )
                await self._emit("step_update", f"{step.title} — complete.")
            else:
                step_evidence_str = ""
                await self._emit("step_update", f"{step.title} — no findings.")

            for artifact_data in buffered_plan_artifacts:
                await self._emit("artifact", artifact_data)

            await self._emit("step_finished", json.dumps({"id": step.id}))

            return {
                "evidence": step_evidence_str,
                "generated_charts": [art.to_dict() for art in buffered_artifacts],
                "current_step": current_step_idx + 1,
                "step_retries": 0,
                "last_step_error": None,
            }

        except Exception as e:
            logger.error("Step execution error", step_id=step.id, error=str(e))
            return {
                "last_step_error": str(e),
            }

    async def _step_error_recovery_node(
        self, state: AgentState, config: RunnableConfig
    ) -> dict:
        """Handles step error logging and increments retries for fault tolerance."""
        current_retries = state.get("step_retries", 0) + 1
        error = state.get("last_step_error", "Unknown execution failure")

        logger.warning(
            "Step failed, triggering fault tolerance recovery",
            retry_count=current_retries,
            error=error,
        )
        await self._emit(
            "step_update", f"Retrying step (Attempt {current_retries})..."
        )

        return {
            "step_retries": current_retries,
            "status": "retrying",
        }

    def _route_execution(
        self, state: AgentState
    ) -> Literal["executor", "step_error_recovery", "synthesizer"]:
        last_error = state.get("last_step_error")
        retries = state.get("step_retries", 0)
        max_retries = state.get("max_retries", 2)

        if last_error and retries < max_retries:
            return "step_error_recovery"

        plan_dict = state.get("plan", {})
        plan = ExecutionPlan.from_dict(plan_dict)
        current_step_idx = state.get("current_step", 0)

        if current_step_idx < len(plan.steps):
            return "executor"

        return "synthesizer"

    async def _synthesizer_node(
        self, state: AgentState, config: RunnableConfig
    ) -> dict:
        logger.info("Phase 3: Synthesizing final answer")
        evidence = state.get("evidence", "").strip()
        if not evidence:
            evidence = "No evidence gathered."

        original_message = state.get("original_message", "")
        dataset_path = state.get("dataset_path")

        user_message = (
            f"Original question: {original_message}\n\n"
            f"Please synthesize the evidence above into a comprehensive final answer."
        )
        if dataset_path:
            user_message = f"[Dataset: {dataset_path}]\n{user_message}"

        synthesis_prompt = SYNTHESIS_SYSTEM_PROMPT.format(evidence=evidence)

        thread_id = config.get("configurable", {}).get("thread_id", "default")
        synth_config = {"configurable": {"thread_id": f"{thread_id}_synthesize"}}

        try:
            async for chunk, metadata in self._synthesis_graph.astream(
                {
                    "messages": [
                        SystemMessage(content=synthesis_prompt),
                        HumanMessage(content=user_message),
                    ],
                    "summary": "",
                },
                stream_mode="messages",
                config=synth_config,
            ):
                if (
                    isinstance(chunk, AIMessageChunk)
                    and chunk.content
                    and metadata.get("langgraph_node") == "agent"
                ):
                    await self._emit("token", chunk.content)
        except Exception as e:
            logger.error("Synthesis failed", error=str(e))
            await self._emit("token", f"\n\n*Error generating final report: {str(e)}*")

        return {"status": "completed"}

    async def stream(
        self,
        message: str,
        thread_id: str,
        dataset_path: str | None = None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        if self._is_simple_question(message):
            logger.info("Simple question detected, using fast path")
            async for event in self._fast_path(message, thread_id, dataset_path):
                yield event
            return

        config = {"configurable": {"thread_id": thread_id}}
        inputs = {
            "original_message": message,
            "dataset_path": dataset_path,
            "messages": [],
            "summary": "",
            "plan": None,
            "evidence": "",
            "generated_charts": [],
            "current_step": 0,
            "run_id": "",
            "step_retries": 0,
            "max_retries": 2,
            "last_step_error": None,
            "status": "planning",
        }

        async for event in self._graph.astream_events(inputs, config, version="v2"):
            if (
                event["event"] == "on_custom_event"
                and event["name"] == "orchestrator_event"
            ):
                data = event["data"]
                yield (data["type"], data["data"])

        yield ("done", "")

    # ── Internal helpers ────────────────────────────────────────────────

    def _is_simple_question(self, message: str) -> bool:
        """Detect trivial conversational messages that don't need a multi-step plan."""
        raw_msg = message

        raw_msg = re.sub(
            r"\n\n\(Please answer in [^\)]+\)", "", raw_msg, flags=re.IGNORECASE
        )
        raw_msg = re.sub(
            r"\n\n\(answer in [^\)]+\)", "", raw_msg, flags=re.IGNORECASE
        )

        if "[Dataset:" in raw_msg and "\n\n" in raw_msg:
            parts = [p.strip() for p in raw_msg.split("\n\n") if p.strip()]
            if parts:
                for part in reversed(parts):
                    if (
                        not part.startswith("[Dataset:")
                        and not part.startswith("CRITICAL INSTRUCTION")
                        and not part.startswith("The dataset above")
                    ):
                        raw_msg = part
                        break

        msg = raw_msg.lower().strip().rstrip("?!.,;:")

        conversational = {
            # English
            "hello",
            "hi",
            "hey",
            "thanks",
            "thank you",
            "ok",
            "okay",
            "yes",
            "no",
            "bye",
            "goodbye",
            "cool",
            "great",
            "awesome",
            "perfect",
            "got it",
            "understood",
            "help",
            # French
            "salut",
            "bonjour",
            "coucou",
            "bonsoir",
            "merci",
            "merci beaucoup",
            "d'accord",
            "daccord",
            "oui",
            "non",
            "ca va",
            "ça va",
            "au revoir",
            "a bientot",
            "à bientôt",
            "super",
            "genial",
            "génial",
            "parfait",
            "compris",
            "qui es-tu",
            "qui es tu",
            "aide",
            "au secours",
        }
        if msg in conversational:
            return True

        simple_starts = (
            "what can you do",
            "how do you work",
            "who are you",
            "help",
            "what is my",
            "what's my",
            "do you remember",
            "who am i",
            "what did we",
            "what was",
            "tell me about myself",
            "my name is",
            "i am",
            "i'm",
            "nice to meet",
            "pleasure",
            "good morning",
            "good afternoon",
            "good evening",
            "how are you",
            "how's it going",
            "what's up",
            "see you",
            "talk to you later",
            "que peux-tu faire",
            "que peux tu faire",
            "que sais-tu faire",
            "que sais tu faire",
            "qu'est-ce que tu peux",
            "qu'est ce que tu peux",
            "qu'est-ce que tu sais",
            "comment tu marches",
            "comment tu fonctionnes",
            "comment ca marche",
            "comment ça marche",
            "qui es-tu",
            "qui es tu",
            "aide-moi",
            "aide moi",
            "mon nom est",
            "je suis",
            "je m'appelle",
            "enchante",
            "enchanté",
            "bonjour",
            "bonsoir",
            "salut",
            "comment vas-tu",
            "comment vas tu",
            "comment ca va",
            "comment ça va",
            "tu te souviens",
            "te souviens-tu",
            "te souviens tu",
        )
        if msg.startswith(simple_starts):
            return True

        analytical_keywords = (
            "analyze",
            "analysis",
            "plot",
            "chart",
            "graph",
            "stat",
            "stats",
            "statistic",
            "describe",
            "correlation",
            "regression",
            "distribution",
            "mean",
            "median",
            "summary",
            "column",
            "row",
            "filter",
            "group",
            "sort",
            "clean",
            "missing",
            "null",
            "outlier",
            "predict",
            "model",
            "compare",
            "analyser",
            "analyse",
            "graphique",
            "graphe",
            "statistique",
            "décrire",
            "decrire",
            "corrélation",
            "correlation",
            "régression",
            "regression",
            "distribution",
            "moyenne",
            "médiane",
            "mediane",
            "résumé",
            "resume",
            "colonne",
            "ligne",
            "filtrer",
            "filtre",
            "grouper",
            "trier",
            "nettoyer",
            "manquant",
            "manquante",
            "anomalie",
            "prédire",
            "predire",
            "modèle",
            "modele",
            "comparer",
        )
        if len(msg) < 25 and not any(kw in msg for kw in analytical_keywords):
            return True

        return False

    def _fallback_plan(self) -> ExecutionPlan:
        """Return a minimal fallback plan when planning fails."""
        return ExecutionPlan(
            title="Analysis",
            steps=[
                PlanStep(1, "Inspect dataset", "Examine data structure.", "inspection"),
                PlanStep(2, "Analyze data", "Perform analysis.", "statistics"),
                PlanStep(3, "Synthesize findings", "Compile report.", "synthesis"),
            ],
        )

    async def _fast_path(
        self,
        message: str,
        thread_id: str,
        dataset_path: str | None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        """Handle simple questions directly without a multi-step plan."""
        config = {"configurable": {"thread_id": thread_id}}
        prompt = message
        if dataset_path and dataset_path not in message:
            prompt = f"[Dataset: {dataset_path}]\n{message}"

        pending_by_id: dict[str, dict] = {}
        pending_by_index: dict[int, dict] = {}

        async for chunk, metadata in self._agent.graph.astream(
            {"messages": [HumanMessage(content=prompt)], "summary": ""},
            stream_mode="messages",
            config=config,
        ):
            self._track_tool_call_chunk(chunk, pending_by_id, pending_by_index)

            if (
                isinstance(chunk, AIMessageChunk)
                and chunk.content
                and metadata.get("langgraph_node") == "agent"
            ):
                yield ("token", chunk.content)
            elif isinstance(chunk, ToolMessage) and chunk.content:
                tool_name, parameters, tc_id, duration_ms = (
                    self._extract_tool_evidence_params(
                        chunk, pending_by_id, pending_by_index
                    )
                )
                raw_result = str(chunk.content)

                evidence_payload = {
                    "step_id": None,
                    "tool_name": tool_name,
                    "tool_call_id": tc_id,
                    "parameters": parameters,
                    "result": raw_result,
                    "status": getattr(chunk, "status", "success"),
                    "execution_time_ms": duration_ms,
                }
                yield ("tool_evidence", json.dumps(evidence_payload))

                content = str(chunk.content)
                for line in content.splitlines():
                    if line.startswith(CHART_ARTIFACT_PREFIX):
                        raw_json = line[len(CHART_ARTIFACT_PREFIX) :]
                        try:
                            artifact = ChartArtifact.from_dict(json.loads(raw_json))
                            yield ("image", artifact.api_url)
                            yield ("chart_artifact", artifact.to_dict())
                        except Exception:
                            pass
                    elif line.startswith(CHART_URL_PREFIX):
                        yield ("image", line[len(CHART_URL_PREFIX) :])
                    elif line.startswith(ARTIFACT_URL_PREFIX):
                        yield ("artifact", line[len(ARTIFACT_URL_PREFIX) :])

        yield ("done", "")

    def _track_tool_call_chunk(
        self,
        chunk,
        pending_by_id: dict[str, dict],
        pending_by_index: dict[int, dict],
    ) -> None:
        tool_calls = getattr(chunk, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                tc_id = (
                    tc.get("id")
                    if isinstance(tc, dict)
                    else getattr(tc, "id", None)
                )
                tc_name = (
                    tc.get("name")
                    if isinstance(tc, dict)
                    else getattr(tc, "name", None)
                )
                tc_args = (
                    tc.get("args")
                    if isinstance(tc, dict)
                    else getattr(tc, "args", None)
                )
                if tc_id:
                    parsed_args = tc_args if isinstance(tc_args, dict) else {}
                    pending_by_id[tc_id] = {
                        "id": tc_id,
                        "name": tc_name or "tool",
                        "args": parsed_args,
                        "args_raw": "",
                        "start_time": time.time(),
                    }

        tool_call_chunks = getattr(chunk, "tool_call_chunks", None)
        if tool_call_chunks:
            for tc in tool_call_chunks:
                if isinstance(tc, dict):
                    idx = tc.get("index", 0)
                    tc_id = tc.get("id")
                    name = tc.get("name")
                    args_fragment = tc.get("args")
                else:
                    idx = getattr(tc, "index", 0)
                    tc_id = getattr(tc, "id", None)
                    name = getattr(tc, "name", None)
                    args_fragment = getattr(tc, "args", None)

                existing = pending_by_index.get(idx)
                if (
                    existing
                    and tc_id
                    and existing.get("id")
                    and existing["id"] != tc_id
                ):
                    existing = None

                if not existing:
                    existing = {
                        "id": tc_id,
                        "name": name or "",
                        "args_raw": "",
                        "start_time": time.time(),
                    }
                    pending_by_index[idx] = existing

                if tc_id:
                    existing["id"] = tc_id
                    pending_by_id[tc_id] = existing
                if name:
                    existing["name"] = name
                if args_fragment:
                    existing["args_raw"] += str(args_fragment)

    def _extract_tool_evidence_params(
        self,
        chunk,
        pending_by_id: dict[str, dict],
        pending_by_index: dict[int, dict],
    ) -> tuple[str, dict, str | None, int | None]:
        tc_id = getattr(chunk, "tool_call_id", None)
        call_info = pending_by_id.pop(tc_id, {}) if tc_id else {}

        for idx, entry in list(pending_by_index.items()):
            if entry.get("id") == tc_id or entry == call_info:
                pending_by_index.pop(idx, None)

        start_time = call_info.get("start_time")
        duration_ms = (
            int((time.time() - start_time) * 1000) if start_time else None
        )
        tool_name = call_info.get("name") or getattr(chunk, "name", "tool")

        parameters = call_info.get("args")
        if parameters is None or not isinstance(parameters, dict) or not parameters:
            args_raw = call_info.get("args_raw", "").strip()
            if args_raw:
                try:
                    parameters = json.loads(args_raw)
                except Exception:
                    parsed = None
                    matches = re.findall(r"\{[^{}]*\}", args_raw)
                    if matches:
                        for candidate in reversed(matches):
                            try:
                                parsed = json.loads(candidate)
                                break
                            except Exception:
                                pass
                    parameters = parsed if isinstance(parsed, dict) else {}
            else:
                parameters = {}

        return tool_name, parameters, tc_id, duration_ms
