"""Generic LLM node — calls the model with bound tools and system prompt."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from ai.models.config import AgentConfig
from ai.state import AgentState
from ai.tool_protocol import ToolProtocol


def make_llm_node(
    state: AgentState,
    config: AgentConfig,
    tools: list[ToolProtocol],
    prompt: str,
    *,
    runnable_config: RunnableConfig | None = None,
) -> dict:
    """Build and invoke the LLM with the current state.

    This is a factory function called by the graph for each step.

    Args:
        state: Current conversation state.
        config: Agent configuration (model, temperature, etc.).
        tools: List of tools to bind to the model.
        prompt: System prompt.
        runnable_config: LangGraph runtime config (passed by the graph).
            Required for token-level streaming via LangGraph callbacks.
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

    # Pass runnable_config so LangGraph's streaming callbacks are attached.
    # Without this, stream_mode="messages" yields the whole response as one chunk.
    response = model.bind_tools(tools).invoke(messages, config=runnable_config)
    return {"messages": [response]}
