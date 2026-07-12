"""Generic LLM node — calls the model with bound tools and system prompt."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from ai.models.config import AgentConfig
from ai.state import AgentState
from ai.tool_protocol import ToolProtocol


def make_llm_node(
    state: AgentState,
    config: AgentConfig,
    tools: list[ToolProtocol],
    prompt: str,
) -> dict:
    """Build and invoke the LLM with the current state.

    This is a factory function called by the graph for each step.
    """
    model = ChatOpenAI(
        model=config.model,
        base_url=config.base_url,
        api_key=config.api_key or "placeholder-key",
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    # Prepend system prompt
    messages = [SystemMessage(content=prompt), *state["messages"]]

    response = model.bind_tools(tools).invoke(messages)
    return {"messages": [response]}
