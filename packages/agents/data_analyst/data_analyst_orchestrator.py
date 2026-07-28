"""Orchestrator — manages the plan → execute → synthesize workflow via LangGraph.

This is the "conductor" from NEXT.md: it coordinates the Planner,
the Agent (for tool execution), and the final synthesis LLM call.

The orchestrator streams structured SSE events via custom events so the frontend can
render a live step-progress UI.
"""

from __future__ import annotations
from pathlib import Path

import json
import re
import time
import uuid

from typing import AsyncGenerator, Literal


from langchain_core.callbacks import adispatch_custom_event
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph

from ai.agent import Agent
from ai.models.config import AgentConfig
from .data_analyst_planner import ExecutionPlan, PlanStep, generate_plan
from ai.logger import get_logger
from ai.state import AgentState
from analysis.charts import ChartArtifact
from tools.visualization.visualization import CHART_ARTIFACT_PREFIX, CHART_URL_PREFIX
from tools.planning import ARTIFACT_URL_PREFIX

logger = get_logger(__name__)


# ── Prompts ────────────────────────────────────────────────────────────

_PROMPTS_DIR = Path(__file__).parent / "prompts"

with open(_PROMPTS_DIR / "step_prompt.md") as f:
    STEP_SYSTEM_PROMPT = f.read()

with open(_PROMPTS_DIR / "synthesis_prompt.md") as f:
    SYNTHESIS_SYSTEM_PROMPT = f.read()

# ── Orchestrator ───────────────────────────────────────────────────────


class Orchestrator:
    """Coordinates the plan → execute → synthesize workflow via LangGraph.

    Usage:
        orch = Orchestrator(agent, config)
        async for event in orch.stream(message, thread_id):
            # event is (event_type, data)
            ...
    """

    def __init__(self, agent: Agent, config: AgentConfig) -> None:
        self._agent = agent
        self._config = config

        # Build the orchestrator graph
        workflow = StateGraph(AgentState)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("executor", self._executor_node)
        workflow.add_node("synthesizer", self._synthesizer_node)

        workflow.add_edge(START, "planner")
        workflow.add_edge("planner", "executor")
        workflow.add_conditional_edges("executor", self._route_execution, {
            "executor": "executor",
            "synthesizer": "synthesizer"
        })
        workflow.add_edge("synthesizer", END)

        self._graph = workflow.compile()

    async def _emit(self, event_type: str, data: str | dict):
        """Helper to dispatch custom events to be caught by stream()."""
        await adispatch_custom_event(
            "orchestrator_event",
            {"type": event_type, "data": data}
        )

    async def _planner_node(self, state: AgentState, config: RunnableConfig) -> dict:
        logger.info("Phase 1: Generating plan")
        original_message = state.get("original_message", "")
        dataset_path = state.get("dataset_path")

        try:
            plan = await generate_plan(original_message, self._config, dataset_path)
        except Exception as e:
            logger.error(
                "Plan generation failed, using fallback", error=str(e))
            plan = self._fallback_plan()

        await self._emit("plan", json.dumps(plan.to_dict()))

        # Generate a run ID for this plan execution to isolate step thread IDs
        run_id = uuid.uuid4().hex[:8]

        return {
            "plan": plan.to_dict(),
            "current_step": 0,
            "evidence": "",
            "generated_charts": [],
            "run_id": run_id,
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

        logger.info("Phase 2: Executing step",
                    step_id=step.id, title=step.title)
        await self._emit("step_started", json.dumps(step.to_dict()))

        if step.tool_hint == "synthesis":
            await self._emit("step_update", "Compiling final report...")
            await self._emit("step_finished", json.dumps({"id": step.id}))
            return {"current_step": current_step_idx + 1}

        # Build step-specific instruction
        user_context = (
            f"## User's Original Request\n{original_message}\n\n"
            if original_message.strip() else ""
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
        # If the planner determined this step needs a visualization, append the
        # chart lifecycle directive with the specific rationale so the step agent
        # knows what kind of chart to generate and why.
        if getattr(step, "needs_visualization", False):
            rationale = getattr(step, "visualization_rationale",
                                "") or "A chart would clarify the findings."
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
        if dataset_path:
            step_instruction = f"[Dataset: {dataset_path}]\n{step_instruction}"

        await self._emit("step_update", f"{step.title}...")

        evidence_tokens: list[str] = []
        buffered_artifacts: list[ChartArtifact] = []
        buffered_plan_artifacts: list[str] = []
        pending_by_id: dict[str, dict] = {}
        pending_by_index: dict[int, dict] = {}

        step_config = {"configurable": {
            "thread_id": f"{thread_id}_run_{run_id}_step_{step.id}"}}

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
                    tool_name, parameters, tc_id, duration_ms = self._extract_tool_evidence_params(chunk, pending_by_id, pending_by_index)
                    raw_result = str(chunk.content)

                    # Emit evidence for traceability
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
                            # Parse the ChartArtifact JSON payload
                            raw_json = line[len(CHART_ARTIFACT_PREFIX):]
                            try:
                                artifact = ChartArtifact.from_dict(
                                    json.loads(raw_json))
                                buffered_artifacts.append(artifact)
                                # Emit image immediately so the UI can display inline
                                await self._emit("image", artifact.api_url)
                                # Emit the full artifact for rich UI rendering
                                await self._emit("chart_artifact", artifact.to_dict())
                            except Exception as parse_err:
                                logger.warning(
                                    "Failed to parse ChartArtifact",
                                    error=str(parse_err),
                                    raw=raw_json[:200],
                                )
                        elif line.startswith(CHART_URL_PREFIX):
                            # Legacy fallback: bare URL with no metadata
                            url = line[len(CHART_URL_PREFIX):]
                            await self._emit("image", url)
                        elif line.startswith(ARTIFACT_URL_PREFIX):
                            buffered_plan_artifacts.append(
                                line[len(ARTIFACT_URL_PREFIX):])


            # Build evidence string: LLM narrative + inline chart summaries
            full_evidence = "".join(evidence_tokens)
            # Append chart evidence summaries inline so the synthesizer
            # knows the title, columns, and insight for each chart
            for art in buffered_artifacts:
                full_evidence += f"\n\n{art.evidence_summary()}\n"
            for artifact_data in buffered_plan_artifacts:
                try:
                    meta = json.loads(artifact_data)
                    full_evidence += f"\n\n[Generated Artifact: {meta.get('filename')}]\n"
                except Exception:
                    pass

            if full_evidence.strip():
                step_evidence_str = f"\n## Step {step.id}: {step.title}\n{full_evidence.strip()}"
                await self._emit("step_update", f"{step.title} — complete.")
            else:
                step_evidence_str = ""
                await self._emit("step_update", f"{step.title} — no findings.")

            for artifact_data in buffered_plan_artifacts:
                await self._emit("artifact", artifact_data)

            result_evidence = step_evidence_str
            result_charts = [art.to_dict() for art in buffered_artifacts]

        except Exception as e:
            logger.error("Step execution error", step_id=step.id, error=str(e))
            await self._emit("step_update", f"Error in step: {str(e)}")
            result_evidence = f"\n## Step {step.id}: {step.title}\n(Execution failed: {str(e)})"
            result_charts = []

        await self._emit("step_finished", json.dumps({"id": step.id}))

        return {
            "evidence": result_evidence,
            "generated_charts": result_charts,
            "current_step": current_step_idx + 1
        }

    def _route_execution(self, state: AgentState) -> Literal["executor", "synthesizer"]:
        plan_dict = state.get("plan", {})
        plan = ExecutionPlan.from_dict(plan_dict)
        current_step_idx = state.get("current_step", 0)

        if current_step_idx < len(plan.steps):
            return "executor"
        return "synthesizer"

    async def _synthesizer_node(self, state: AgentState, config: RunnableConfig) -> dict:
        logger.info("Phase 3: Synthesizing final answer")
        # Charts are already displayed inline by the UI as they are emitted
        # during execution. The synthesizer does NOT pre-dump charts at the top;
        # instead the evidence manifest contains [Chart: ...] references inline
        # with each step so the LLM can reference them in context.
        evidence = state.get("evidence", "").strip()
        if not evidence:
            evidence = "No evidence gathered."

        original_message = state.get("original_message", "")
        dataset_path = state.get("dataset_path")
        thread_id = config.get("configurable", {}).get("thread_id", "default")

        user_message = (
            f"Original question: {original_message}\n\n"
            f"Please synthesize the evidence above into a comprehensive final answer."
        )
        if dataset_path:
            user_message = f"[Dataset: {dataset_path}]\n{user_message}"

        synthesis_prompt = SYNTHESIS_SYSTEM_PROMPT.format(evidence=evidence)
        synth_config = {"configurable": {
            "thread_id": f"{thread_id}_synthesize"}}

        try:
            async for chunk, metadata in self._agent.graph.astream(
                {
                    "messages": [
                        SystemMessage(content=synthesis_prompt),
                        HumanMessage(content=user_message)
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
                elif isinstance(chunk, ToolMessage) and chunk.content:
                    content = str(chunk.content)
                    for line in content.splitlines():
                        if line.startswith(CHART_ARTIFACT_PREFIX):
                            raw_json = line[len(CHART_ARTIFACT_PREFIX):]
                            try:
                                artifact = ChartArtifact.from_dict(
                                    json.loads(raw_json))
                                await self._emit("image", artifact.api_url)
                                await self._emit("chart_artifact", artifact.to_dict())
                            except Exception as parse_err:
                                logger.warning(
                                    "Synthesizer: failed to parse ChartArtifact",
                                    error=str(parse_err),
                                )
                        elif line.startswith(CHART_URL_PREFIX):
                            await self._emit("image", line[len(CHART_URL_PREFIX):])
                        elif line.startswith(ARTIFACT_URL_PREFIX):
                            await self._emit("artifact", line[len(ARTIFACT_URL_PREFIX):])
        except Exception as e:
            logger.error("Synthesis failed", error=str(e))
            await self._emit("token", f"\n\n*Error generating final report: {str(e)}*")

        return {}

    async def stream(
        self,
        message: str,
        thread_id: str,
        dataset_path: str | None = None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        user_msg_lower = message.lower().strip()

        if self._is_simple_question(user_msg_lower):
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
        }

        async for event in self._graph.astream_events(inputs, config, version="v2"):
            if event["event"] == "on_custom_event" and event["name"] == "orchestrator_event":
                data = event["data"]
                yield (data["type"], data["data"])

        yield ("done", "")

    # ── Internal methods ────────────────────────────────────────────────

    def _is_simple_question(self, message: str) -> bool:
        """Detect trivial conversational messages that don't need a plan."""
        msg = message.lower().strip().rstrip("?!.")
        conversational = {"hello", "hi", "hey", "thanks",
                          "thank you", "ok", "okay", "yes", "no", "bye", "goodbye"}
        if msg in conversational:
            return True

        simple_starts = (
            "what can you do", "how do you work",
            "who are you", "help",
            "what is my", "what's my",         # personal info (name, etc.)
            "do you remember",                   # memory recall
            "who am i",                          # identity
            "what did we", "what was",           # conversation recall
            "tell me about myself",              # personal summary
            "my name is", "i am", "i'm",         # self-introductions
            "nice to meet", "pleasure",          # pleasantries
            "good morning", "good afternoon",    # time-based greetings
            "good evening", "how are you",       # social
            "how's it going", "what's up",       # casual
            "see you", "talk to you later",      # farewells
        )
        if msg.startswith(simple_starts):
            return True
        return False

    def _fallback_plan(self) -> ExecutionPlan:
        """Return a minimal fallback plan when planning fails."""
        from .data_analyst_planner import PlanStep
        return ExecutionPlan(
            title="Analysis",
            steps=[
                PlanStep(1, "Inspect dataset",
                         "Examine data structure.", "inspection"),
                PlanStep(2, "Analyze data", "Perform analysis.", "statistics"),
                PlanStep(3, "Synthesize findings",
                         "Compile report.", "synthesis"),
            ],
        )

    async def _fast_path(
        self,
        message: str,
        thread_id: str,
        dataset_path: str | None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        """Handle simple questions directly without a plan."""
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
                tool_name, parameters, tc_id, duration_ms = self._extract_tool_evidence_params(chunk, pending_by_id, pending_by_index)
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

        yield ("done", "")

    def _track_tool_call_chunk(self, chunk, pending_by_id: dict[str, dict], pending_by_index: dict[int, dict]) -> None:
        """Accumulate tool calls and parameter fragments from streaming message chunks."""
        # 1. Handle complete tool_calls attribute (if available)
        tool_calls = getattr(chunk, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                tc_id = tc.get("id") if isinstance(tc, dict) else getattr(tc, "id", None)
                tc_name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                tc_args = tc.get("args") if isinstance(tc, dict) else getattr(tc, "args", None)
                if tc_id:
                    parsed_args = tc_args if isinstance(tc_args, dict) else {}
                    pending_by_id[tc_id] = {
                        "id": tc_id,
                        "name": tc_name or "tool",
                        "args": parsed_args,
                        "args_raw": "",
                        "start_time": time.time(),
                    }

        # 2. Handle streaming tool_call_chunks attribute
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

                # Reset index entry if a new tool call ID is starting at this index
                existing = pending_by_index.get(idx)
                if existing and tc_id and existing.get("id") and existing["id"] != tc_id:
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
        """Extract tool evidence parameters and execution timing for a completed ToolMessage."""
        tc_id = getattr(chunk, "tool_call_id", None)
        call_info = pending_by_id.pop(tc_id, {}) if tc_id else {}

        # Remove completed tool call from pending_by_index map
        for idx, entry in list(pending_by_index.items()):
            if entry.get("id") == tc_id or entry == call_info:
                pending_by_index.pop(idx, None)

        start_time = call_info.get("start_time")
        duration_ms = int((time.time() - start_time) * 1000) if start_time else None
        tool_name = call_info.get("name") or getattr(chunk, "name", "tool")

        parameters = call_info.get("args")
        if parameters is None or not isinstance(parameters, dict) or not parameters:
            args_raw = call_info.get("args_raw", "").strip()
            if args_raw:
                try:
                    parameters = json.loads(args_raw)
                except Exception:
                    # If args_raw contains concatenated JSONs (e.g. {"a":1}{"b":2}), parse the last complete valid JSON object!
                    parsed = None
                    matches = re.findall(r'\{[^{}]*\}', args_raw)
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
