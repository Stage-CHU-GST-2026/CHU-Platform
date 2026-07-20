"""Planner module — generates structured execution plans from user requests.

The planner calls the LLM with a specialized planning prompt and
returns a list of execution steps. Each step has an id, title,
description, and an optional list of expected tool categories.
"""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ai.models.config import AgentConfig
from ai.logger import get_logger

logger = get_logger(__name__)

from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "prompts"
with open(_PROMPTS_DIR / "planner_prompt.md") as f:
    PLANNER_SYSTEM_PROMPT = f.read()


class PlanStep:
    """A single execution step in a plan."""

    def __init__(
        self,
        id: int,
        title: str,
        description: str,
        tool_hint: str = "",
        needs_visualization: bool = False,
        visualization_rationale: str = "",
    ) -> None:
        self.id = id
        self.title = title
        self.description = description
        self.tool_hint = tool_hint
        self.needs_visualization = needs_visualization
        self.visualization_rationale = visualization_rationale

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "tool_hint": self.tool_hint,
            "needs_visualization": self.needs_visualization,
            "visualization_rationale": self.visualization_rationale,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlanStep":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            tool_hint=data.get("tool_hint", ""),
            needs_visualization=data.get("needs_visualization", False),
            visualization_rationale=data.get("visualization_rationale", ""),
        )


class ExecutionPlan:
    """A complete execution plan with a title and ordered steps."""

    def __init__(self, title: str, steps: list[PlanStep]) -> None:
        self.title = title
        self.steps = steps

    def to_dict(self) -> dict:
        return {
            "plan_title": self.title,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExecutionPlan":
        steps = [PlanStep.from_dict(s) for s in data.get("steps", [])]
        return cls(title=data.get("plan_title", "Analysis Plan"), steps=steps)


def _extract_json(text: str) -> str:
    """Extract a JSON object from LLM output that may contain markdown fences."""
    # Try to find JSON in a code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    # Try to find raw JSON
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0).strip()
    return text.strip()


async def generate_plan(
    user_message: str,
    config: AgentConfig,
    dataset_path: str | None = None,
) -> ExecutionPlan:
    """Call the LLM to generate an execution plan for the user's request.

    Args:
        user_message: The user's original request.
        config: Model configuration.
        dataset_path: Optional path to a dataset file.

    Returns:
        An ExecutionPlan with ordered steps.
    """
    model = ChatOpenAI(
        model=config.model,
        base_url=config.base_url,
        api_key=config.api_key or "placeholder-key",
        temperature=0,  # Deterministic planning
        max_tokens=config.max_tokens,
    )

    # Build the planning message
    context = user_message
    if dataset_path and dataset_path not in user_message:
        context = f"[Dataset: {dataset_path}]\n{user_message}"

    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(
            content=f"Generate an execution plan for this request:\n\n{context}"),
    ]

    logger.info("Generating execution plan")
    response = await model.ainvoke(messages)
    raw_text = response.content if hasattr(
        response, "content") else str(response)

    try:
        json_str = _extract_json(raw_text)
        data = json.loads(json_str)
        plan = ExecutionPlan.from_dict(data)
        logger.info("Plan generated", steps=len(plan.steps))
        return plan
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(
            "Failed to parse plan JSON, using fallback", error=str(e))
        # Fallback: create a simple default plan
        steps = [
            PlanStep(1, "Inspect dataset",
                     "Examine the dataset structure and contents.", "inspection"),
            PlanStep(2, "Analyze data",
                     "Perform the requested analysis.", "statistics"),
            PlanStep(3, "Synthesize findings",
                     "Compile results into a clear report.", "synthesis"),
        ]
        return ExecutionPlan(title="Data Analysis", steps=steps)
