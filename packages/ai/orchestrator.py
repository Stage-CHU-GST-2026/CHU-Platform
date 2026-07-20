"""Orchestrator — manages the plan → execute → synthesize workflow via LangGraph.

This is the "conductor" from NEXT.md: it coordinates the Planner,
the Agent (for tool execution), and the final synthesis LLM call.

The orchestrator streams structured SSE events via custom events so the frontend can
render a live step-progress UI.
"""

from __future__ import annotations

import json
import uuid
from typing import AsyncGenerator, Literal

from langchain_core.callbacks import adispatch_custom_event
from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph

from ai.agent import Agent
from ai.models.config import AgentConfig
from ai.planner import ExecutionPlan, PlanStep, generate_plan
from ai.logger import get_logger
from ai.state import AgentState
from tools.visualization.visualization import CHART_URL_PREFIX
from tools.planning import ARTIFACT_URL_PREFIX

logger = get_logger(__name__)

# ── Step-specific prompts ──────────────────────────────────────────────

STEP_SYSTEM_PROMPT = """You are an expert data analyst executing a specific step in an analysis plan.

## Current Task
{step_title}: {step_description}

## Context
This is step {step_id} of a multi-step analysis. Focus ONLY on this step.
Do NOT try to do everything at once. Other steps will handle other tasks.

## Rules
- Use the available tools to gather evidence for this specific step.
- VERY IMPORTANT: Call tools sequentially. Do NOT call the same tool or multiple tools in parallel.
- Be thorough but focused.
- Report what you found clearly and concisely.
- If a tool call fails, note it and move on.
- Do NOT make a plan or list next steps — just execute this step."""

SYNTHESIS_SYSTEM_PROMPT = """You are an expert data analyst writing a final report.

## Context
All analysis steps have been completed. Below is the evidence gathered from each step.
Your job is to synthesize this evidence into a clear, comprehensive final answer.

## Evidence Gathered
{evidence}

## Rules
- Every conclusion MUST be supported by the evidence above.
- Never fabricate or guess statistics not present in the evidence.
- Present findings in a logical order.
- Use markdown formatting for clarity (headings, lists, tables).
- Any generated charts are automatically displayed above your text, so you do NOT need to embed image links yourself. Refer to them as "the chart above".
- Include specific numbers and statistics where available.
- If evidence is insufficient for any conclusion, explicitly say so.
- Do NOT call any more tools — just write the final report."""

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
            logger.error("Plan generation failed, using fallback", error=str(e))
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

        logger.info("Phase 2: Executing step", step_id=step.id, title=step.title)
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
        if dataset_path:
            step_instruction = f"[Dataset: {dataset_path}]\n{step_instruction}"

        await self._emit("step_update", f"{step.title}...")

        evidence_tokens: list[str] = []
        buffered_images: list[str] = []
        buffered_artifacts: list[str] = []

        step_config = {"configurable": {"thread_id": f"{thread_id}_run_{run_id}_step_{step.id}"}}

        try:
            async for chunk, metadata in self._agent.graph.astream(
                {
                    "messages": [HumanMessage(content=step_instruction)],
                    "summary": "",
                },
                stream_mode="messages",
                config=step_config,
            ):
                if (
                    isinstance(chunk, AIMessageChunk)
                    and chunk.content
                    and metadata.get("langgraph_node") == "agent"
                ):
                    evidence_tokens.append(chunk.content)
                    await self._emit("step_token", chunk.content)

                elif isinstance(chunk, ToolMessage) and chunk.content:
                    content = str(chunk.content)
                    for line in content.splitlines():
                        if line.startswith(CHART_URL_PREFIX):
                            buffered_images.append(line[len(CHART_URL_PREFIX):])
                        elif line.startswith(ARTIFACT_URL_PREFIX):
                            buffered_artifacts.append(line[len(ARTIFACT_URL_PREFIX):])

            full_evidence = "".join(evidence_tokens)
            for img_url in buffered_images:
                full_evidence += f"\n\n[Generated Chart URL: {img_url}]\n\n"
            for artifact_data in buffered_artifacts:
                try:
                    meta = json.loads(artifact_data)
                    full_evidence += f"\n\n[Generated Artifact: {meta.get('filename')}]\n\n"
                except Exception:
                    pass

            if full_evidence.strip():
                step_evidence_str = f"\n## Step {step.id}: {step.title}\n{full_evidence.strip()}"
                await self._emit("step_update", f"{step.title} — complete.")
            else:
                step_evidence_str = ""
                await self._emit("step_update", f"{step.title} — no findings.")

            for img_url in buffered_images:
                await self._emit("image", img_url)
            for artifact_data in buffered_artifacts:
                await self._emit("artifact", artifact_data)

            result_evidence = step_evidence_str

        except Exception as e:
            logger.error("Step execution error", step_id=step.id, error=str(e))
            await self._emit("step_update", f"Error in step: {str(e)}")
            result_evidence = f"\n## Step {step.id}: {step.title}\n(Execution failed: {str(e)})"

        await self._emit("step_finished", json.dumps({"id": step.id}))

        return {
            "evidence": result_evidence,
            "generated_charts": buffered_images,
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
        
        generated_charts = state.get("generated_charts", [])
        for chart_url in generated_charts:
            await self._emit("token", f"![Generated Chart]({chart_url})\n\n")
            
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
        synth_config = {"configurable": {"thread_id": f"{thread_id}_synthesize"}}

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
                        if line.startswith(CHART_URL_PREFIX):
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
        meta_starts = ("what can you do", "how do you work",
                       "who are you", "help")
        if msg.startswith(meta_starts):
            return True
        return False

    def _fallback_plan(self) -> ExecutionPlan:
        """Return a minimal fallback plan when planning fails."""
        from ai.planner import PlanStep
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

        async for chunk, metadata in self._agent.graph.astream(
            {"messages": [HumanMessage(content=prompt)], "summary": ""},
            stream_mode="messages",
            config=config,
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
                    if line.startswith(CHART_URL_PREFIX):
                        yield ("image", line[len(CHART_URL_PREFIX):])
                    elif line.startswith(ARTIFACT_URL_PREFIX):
                        yield ("artifact", line[len(ARTIFACT_URL_PREFIX):])

        yield ("done", "")
