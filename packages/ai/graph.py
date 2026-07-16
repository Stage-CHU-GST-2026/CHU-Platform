"""LangGraph workflow builder — generic, no hardcoded tools."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.store.base import BaseStore

from ai.models.config import AgentConfig
from ai.nodes.llm import make_llm_node
from ai.nodes.memory import make_summary_node
from ai.nodes.tools import make_tools_node
from ai.state import AgentState
from ai.tool_protocol import ToolProtocol


def build_graph(
    config: AgentConfig,
    tools: list[ToolProtocol],
    prompt: str = "You are a helpful assistant.",
    checkpointer: InMemorySaver | None = None,
    store: BaseStore | None = None,
) -> StateGraph:
    """Build a compiled LangGraph workflow.

    Args:
        config: Model configuration.
        tools: List of tool objects to make available to the LLM.
        prompt: System prompt for the LLM.
        checkpointer: Optional checkpointer for multi-turn conversations.
        store: Optional store for long-term cross-conversation memory.

    Returns:
        Compiled StateGraph.
    """

    def call_model(state: AgentState, _config: RunnableConfig | None = None):
        return make_llm_node(
            state=state,
            config=config,
            tools=tools,
            prompt=prompt,
            runnable_config=_config,
        )

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return "summarize"

    tools_node = make_tools_node(tools)
    summarize_node = make_summary_node(config)

    builder = StateGraph(AgentState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", tools_node)
    builder.add_node("summarize", summarize_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {
        "tools": "tools",
        "summarize": "summarize",
    })
    builder.add_edge("tools", "agent")
    builder.add_edge("summarize", END)

    return builder.compile(checkpointer=checkpointer, store=store)
