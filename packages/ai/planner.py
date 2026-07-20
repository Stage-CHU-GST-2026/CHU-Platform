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

PLANNER_SYSTEM_PROMPT = """You are an execution planner for a data analysis agent. Your job is to
break down a user's request into a clear, ordered list of execution steps.

## Rules

1. Produce exactly the steps needed — no more, no less.
2. Each step must be actionable: it describes what to DO, not what to know.
3. Steps should be in logical order (inspect before analyze, clean before stats).
4. Include a final "Synthesize findings" step.
5. Keep step titles short (2-5 words) and descriptions clear (1 sentence).
6. Visualization is evidence, NOT a standalone step. If an analytical step
   benefits from a chart, set `needs_visualization: true` and explain why
   in `visualization_rationale`. DO NOT add a separate "Generate charts" step.

## Output Format

Return ONLY a JSON object with this exact structure:
```json
{
  "plan_title": "Short title for the overall plan",
  "steps": [
    {
      "id": 1,
      "title": "Inspect dataset",
      "description": "Load the dataset and examine its structure, columns, and types.",
      "tool_hint": "inspection",
      "needs_visualization": false,
      "visualization_rationale": ""
    }
  ]
}
```

## Tool Categories (for tool_hint)

- inspection: describe_dataset, dataset_summary, list_columns, column_info, dataset_head, dataset_shape, list_datasets
- quality: missing_values, duplicates
- cleaning: drop_columns
- statistics: mean, median, min, max, std, quantiles
- aggregation: aggregate, filter, sort
- relationships: correlation, outliers
- visualization: generate_chart, correlation_heatmap (use ONLY when the step is PURELY visual)
- planning: create_blueprint
- synthesis: no tools needed (just thinking/writing)

## When to set needs_visualization: true

Set `needs_visualization: true` when a chart would reveal patterns the numbers alone cannot:
- Comparing values across categories → bar chart (combine with aggregation step)
- Showing a distribution → histogram or KDE (combine with statistics step)
- Revealing a relationship between two numeric columns → scatter (combine with correlation step)
- Showing a correlation matrix → heatmap (combine with relationships step)

Never set needs_visualization for inspection or quality steps.

## Examples

User: "Analyze sales.csv"
```json
{
  "plan_title": "Sales Data Analysis",
  "steps": [
    {"id": 1, "title": "Inspect dataset", "description": "Load sales.csv and examine its structure, columns, and row count.", "tool_hint": "inspection", "needs_visualization": false, "visualization_rationale": ""},
    {"id": 2, "title": "Check data quality", "description": "Scan for missing values, duplicates, and outliers.", "tool_hint": "quality", "needs_visualization": false, "visualization_rationale": ""},
    {"id": 3, "title": "Compute statistics", "description": "Calculate key statistics: mean, median, std for numeric columns and visualize their distributions.", "tool_hint": "statistics", "needs_visualization": true, "visualization_rationale": "Histograms will show whether numeric columns are skewed or normally distributed."},
    {"id": 4, "title": "Category comparison", "description": "Aggregate revenue by category and compare them visually.", "tool_hint": "aggregation", "needs_visualization": true, "visualization_rationale": "A bar chart will make relative category sizes immediately clear."},
    {"id": 5, "title": "Analyze relationships", "description": "Check correlations between numeric variables and visualize the correlation matrix.", "tool_hint": "relationships", "needs_visualization": true, "visualization_rationale": "A correlation heatmap will reveal which variables are strongly related."},
    {"id": 6, "title": "Synthesize findings", "description": "Compile all evidence into a clear summary report.", "tool_hint": "synthesis", "needs_visualization": false, "visualization_rationale": ""}
  ]
}
```

User: "What columns are in the dataset?"
```json
{
  "plan_title": "Dataset Inspection",
  "steps": [
    {"id": 1, "title": "Inspect dataset", "description": "Load the dataset and list all columns with their types.", "tool_hint": "inspection", "needs_visualization": false, "visualization_rationale": ""},
    {"id": 2, "title": "Synthesize findings", "description": "Present the column listing clearly.", "tool_hint": "synthesis", "needs_visualization": false, "visualization_rationale": ""}
  ]
}
```"""


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
