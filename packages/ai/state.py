import operator
from typing import Annotated, Any

from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    summary: str
    # ── Orchestrator fields ─────────────────────────────────────────
    plan: dict | None          # The execution plan (serialized ExecutionPlan)
    evidence: Annotated[str, operator.add] # Accumulated evidence from executed steps
    current_step: int          # Index of the currently executing step (0-based)
    original_message: str      # The user's original request
    dataset_path: str | None   # Optional dataset path
    run_id: str                # Unique ID for the current execution run
