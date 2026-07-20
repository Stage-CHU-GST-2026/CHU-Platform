"""Orchestrator — manages the plan → execute → synthesize workflow.

This is the "conductor" from NEXT.md: it coordinates the Planner,
the Agent (for tool execution), and the final synthesis LLM call.

The orchestrator streams structured SSE events so the frontend can
render a live step-progress UI.
"""

from __future__ import annotations

import json
import uuid
from typing import AsyncGenerator

from langchain_core.messages import AIMessageChunk, HumanMessage, ToolMessage

from ai.agent import Agent
from ai.models.config import AgentConfig
from ai.planner import ExecutionPlan, PlanStep, generate_plan
from ai.logger import get_logger
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
    """Coordinates the plan → execute → synthesize workflow.

    Usage:
        orch = Orchestrator(agent, config)
        async for event in orch.stream(message, thread_id):
            # event is (event_type, data)
            ...
    """

    def __init__(self, agent: Agent, config: AgentConfig) -> None:
        self._agent = agent
        self._config = config

    async def stream(
        self,
        message: str,
        thread_id: str,
        dataset_path: str | None = None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        """Execute the full plan→execute→synthesize workflow, streaming events.

        Yields:
            ("plan", dict)          — the full execution plan
            ("step_started", dict)  — a step is starting {id, title}
            ("step_update", str)    — progress message within a step
            ("step_finished", dict) — a step completed {id}
            ("image", str)          — chart URL
            ("artifact", str)       — plan artifact JSON
            ("token", str)          — text token from final synthesis
            ("done", str)           — stream complete
        """
        user_msg_lower = message.lower().strip()

        # ── Simple questions skip the full plan workflow ────────────────
        if self._is_simple_question(user_msg_lower):
            logger.info("Simple question detected, using fast path")
            async for event in self._fast_path(message, thread_id, dataset_path):
                yield event
            return

        # ── Phase 1: Generate plan ─────────────────────────────────────
        logger.info("Phase 1: Generating plan")
        try:
            plan = await generate_plan(message, self._config, dataset_path)
        except Exception as e:
            logger.error(
                "Plan generation failed, using fallback", error=str(e))
            plan = self._fallback_plan()

        yield ("plan", json.dumps(plan.to_dict()))

        # A unique ID for this specific run (user query). We use this to isolate
        # step memory so that step 1 of this plan doesn't inherit the LangGraph
        # state of step 1 from a previous plan in the same conversation.
        run_id = uuid.uuid4().hex[:8]

        # ── Phase 2: Execute each step ─────────────────────────────────
        evidence_parts: list[str] = []
        all_generated_charts: list[str] = []

        for step in plan.steps:
            logger.info("Phase 2: Executing step",
                        step_id=step.id, title=step.title)

            # Signal step start
            yield ("step_started", json.dumps(step.to_dict()))

            # If this is the synthesis step, skip tool execution
            if step.tool_hint == "synthesis":
                yield ("step_update", "Compiling final report...")
                yield ("step_finished", json.dumps({"id": step.id}))
                continue

            # Execute the step via the agent
            step_evidence = ""
            try:
                async for event_type, data in self._execute_step(
                    step=step,
                    thread_id=thread_id,
                    run_id=run_id,
                    original_message=message,
                    dataset_path=dataset_path,
                ):
                    if event_type == "step_evidence":
                        # Internal: collect evidence for the synthesis prompt
                        step_evidence += str(data)
                    elif event_type == "step_token":
                        # Live text token from the step — forward to frontend
                        yield ("step_token", str(data))
                    elif event_type == "step_update":
                        yield ("step_update", str(data))
                    elif event_type == "image":
                        all_generated_charts.append(str(data))
                        yield ("image", str(data))
                    elif event_type == "artifact":
                        yield ("artifact", str(data))

                if step_evidence.strip():
                    evidence_parts.append(
                        f"## Step {step.id}: {step.title}\n{step_evidence.strip()}"
                    )

            except Exception as e:
                logger.error("Step execution failed",
                             step_id=step.id, error=str(e))
                yield ("step_update", f"Error in step: {str(e)}")
                evidence_parts.append(
                    f"## Step {step.id}: {step.title}\n(Execution failed: {str(e)})"
                )

            # Signal step complete
            yield ("step_finished", json.dumps({"id": step.id}))

        # ── Phase 3: Synthesize final answer ────────────────────────────
        logger.info("Phase 3: Synthesizing final answer")

        # Pre-inject any generated charts as standard text tokens so they appear 
        # properly formatted at the top of the final response bubble.
        for chart_url in all_generated_charts:
            yield ("token", f"![Generated Chart]({chart_url})\n\n")

        combined_evidence = "\n\n".join(
            evidence_parts) if evidence_parts else "No evidence gathered."

        try:
            async for event_type, data in self._synthesize(
                evidence=combined_evidence,
                original_question=message,
                thread_id=thread_id,
                dataset_path=dataset_path,
            ):
                yield (event_type, data)
        except Exception as e:
            logger.error("Synthesis failed", error=str(e))
            yield ("token", f"\n\n*Error generating final report: {str(e)}*")

        # ── Done ────────────────────────────────────────────────────────
        yield ("done", "")

    # ── Internal methods ────────────────────────────────────────────────

    def _is_simple_question(self, message: str) -> bool:
        """Detect trivial conversational messages that don't need a plan.

        Only matches very generic greetings / meta-questions, NOT
        data-analysis questions (even short ones like "what columns?").
        """
        msg = message.lower().strip().rstrip("?!.")
        # Very short conversational messages
        conversational = {"hello", "hi", "hey", "thanks",
                          "thank you", "ok", "okay", "yes", "no", "bye", "goodbye"}
        if msg in conversational:
            return True
        # Meta questions about capabilities
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

        # Stream directly from the agent
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

    async def _execute_step(
        self,
        step: PlanStep,
        thread_id: str,
        run_id: str,
        original_message: str = "",
        dataset_path: str | None = None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        """Execute a single plan step via the agent.

        Yields:
            ("step_evidence", str) — internal: step findings for the synthesis prompt
            ("step_update", str)   — progress message for the frontend
            ("step_token", str)    — live text token streamed during step execution
            ("image", str)         — chart URL
            ("artifact", str)      — plan artifact JSON
        """
        config = {"configurable": {"thread_id": f"{thread_id}_run_{run_id}_step_{step.id}"}}

        # Each step runs in its own isolated thread (no shared memory), so the
        # original user request MUST be embedded in the instruction — otherwise
        # the agent has no idea which dataset or scope the user intended and will
        # fall back to listing and inspecting every available dataset.
        user_context = (
            f"## User's Original Request\n{original_message}\n\n"
            if original_message.strip()
            else ""
        )

        # Build step-specific instruction
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

        yield ("step_update", f"{step.title}...")

        evidence_tokens: list[str] = []
        # Images/artifacts are buffered and emitted AFTER all step text has
        # streamed.  This is required because LangGraph's execution order is
        # always:  agent (tool-call decision) → tools (ToolMessage) → agent
        # (interpretation text).  The ToolMessage — which carries the image
        # URL — is therefore produced BEFORE the LLM has written a single word
        # of interpretation, so emitting images immediately would place them
        # above the text that describes them.  Buffering and flushing after the
        # astream loop guarantees text → images order every time.
        buffered_images: list[str] = []
        buffered_artifacts: list[str] = []

        try:
            async for chunk, metadata in self._agent.graph.astream(
                {
                    "messages": [HumanMessage(content=step_instruction)],
                    "summary": "",
                },
                stream_mode="messages",
                config=config,
            ):
                if (
                    isinstance(chunk, AIMessageChunk)
                    and chunk.content
                    and metadata.get("langgraph_node") == "agent"
                ):
                    # Stream interpretation text live as it is generated.
                    evidence_tokens.append(chunk.content)
                    yield ("step_token", chunk.content)

                elif isinstance(chunk, ToolMessage) and chunk.content:
                    # Buffer images/artifacts — do NOT emit yet.
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
                yield ("step_evidence", full_evidence)
                yield ("step_update", f"{step.title} — complete.")
            else:
                yield ("step_update", f"{step.title} — no findings.")

            # Flush buffered images and artifacts now that all text has
            # been streamed, so they appear below their textual context.
            for img_url in buffered_images:
                yield ("image", img_url)
            for artifact_data in buffered_artifacts:
                yield ("artifact", artifact_data)

        except Exception as e:
            logger.error("Step execution error", step_id=step.id, error=str(e))
            yield ("step_evidence", f"(Step '{step.title}' encountered an error: {str(e)})")

    async def _synthesize(
        self,
        evidence: str,
        original_question: str,
        thread_id: str,
        dataset_path: str | None = None,
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        """Generate the final synthesized answer, streaming token by token."""
        config = {"configurable": {"thread_id": f"{thread_id}_synthesize"}}

        synthesis_prompt = SYNTHESIS_SYSTEM_PROMPT.format(evidence=evidence)

        user_message = (
            f"Original question: {original_question}\n\n"
            f"Please synthesize the evidence above into a comprehensive final answer."
        )
        if dataset_path:
            user_message = f"[Dataset: {dataset_path}]\n{user_message}"

        # Use astream for token-by-token output
        try:
            async for chunk, metadata in self._agent.graph.astream(
                {
                    "messages": [HumanMessage(content=user_message)],
                    "summary": "",
                },
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

        except Exception as e:
            logger.error("Synthesis error", error=str(e))
            yield ("token", f"\n\n*Error generating final report: {str(e)}*")
