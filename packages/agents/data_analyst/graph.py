"""LangGraph workflow builder for Data Analyst agent."""

from __future__ import annotations

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.store.base import BaseStore

from .config import DataAnalystConfig
from .logger import get_logger
from .nodes import make_llm_node, make_summary_node, make_tools_node
from .state import DataAnalystState

logger = get_logger(__name__)


def build_data_analyst_graph(
    config: DataAnalystConfig,
    tools: list,
    prompt: str = "You are a helpful data analyst.",
    checkpointer: InMemorySaver | None = None,
    store: BaseStore | None = None,
) -> StateGraph:
    """Build a compiled LangGraph workflow for Data Analyst."""

    def call_model(state: DataAnalystState, _config: RunnableConfig | None = None):
        return make_llm_node(
            state=state,
            config=config,
            tools=tools,
            prompt=prompt,
            runnable_config=_config,
        )

    def should_continue(state: DataAnalystState) -> str:
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            tool_names = [tc["name"] for tc in last.tool_calls]
            logger.info("Agent requested tools", tools=tool_names)
            return "tools"
        logger.info("Agent finished thinking, moving to summarize")
        return "summarize"

    tools_node = make_tools_node(tools)
    summarize_node = make_summary_node(config)

    builder = StateGraph(DataAnalystState)
    builder.add_node("agent", call_model)

    def wrapped_tools_node(state: DataAnalystState):
        logger.info("Executing tools step")
        result = tools_node.invoke(state)
        logger.info("Tools execution completed")
        return result

    builder.add_node("tools", wrapped_tools_node)
    builder.add_node("summarize", summarize_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "summarize": "summarize",
        },
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("summarize", END)

    return builder.compile(checkpointer=checkpointer, store=store)


# Alias for backward compatibility
build_graph = build_data_analyst_graph
