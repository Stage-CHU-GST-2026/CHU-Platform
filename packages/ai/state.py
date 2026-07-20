from typing import Annotated, Any

from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    summary: str
    # ── Orchestrator fields ─────────────────────────────────────────
    plan: dict | None          # The execution plan (serialized ExecutionPlan)
    evidence: str              # Accumulated evidence from executed steps
    # Index of the currently executing step (0-based)
    current_step: int
