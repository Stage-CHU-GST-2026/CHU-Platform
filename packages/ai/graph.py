"""LangGraph workflow builder — generic, no hardcoded tools."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from ai.models.config import AgentConfig
from ai.nodes.llm import make_llm_node
from ai.nodes.tools import make_tools_node
from ai.state import AgentState
from ai.tool_protocol import ToolProtocol


def build_graph(
    config: AgentConfig,
    tools: list[ToolProtocol],
    prompt: str = "You are a helpful assistant.",
) -> StateGraph:
    """Build a compiled LangGraph workflow.

    Args:
        config: Model configuration.
        tools: List of tool objects to make available to the LLM.
        prompt: System prompt for the LLM.

    Returns:
        Compiled StateGraph.
    """

    def call_model(state: AgentState):
        return make_llm_node(state=state, config=config, tools=tools, prompt=prompt)

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return END

    tools_node = make_tools_node(tools)

    builder = StateGraph(AgentState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", tools_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {
                                  "tools": "tools", END: END})
    builder.add_edge("tools", "agent")

    return builder.compile()
