"""State definition for Data Analyst agent."""

from __future__ import annotations

import operator
from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class DataAnalystState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    summary: str
    # ── Orchestrator fields ─────────────────────────────────────────
    plan: dict | None  # The execution plan (serialized ExecutionPlan)
    evidence: Annotated[str, operator.add]  # Accumulated evidence from executed steps
    generated_charts: Annotated[list[dict], operator.add]  # ChartArtifact dicts generated across steps
    current_step: int  # Index of the currently executing step (0-based)
    original_message: str  # The user's original request
    dataset_path: str | None  # Optional dataset path
    run_id: str  # Unique ID for the current execution run
    # ── Fault tolerance & state management ────────────────────────
    step_retries: int  # Consecutive retries for current step
    max_retries: int  # Maximum retries per step before proceeding/failing
    last_step_error: Optional[str]  # Traceback or error description for self-correction
    status: Literal["planning", "executing", "retrying", "synthesizing", "completed", "failed"]
