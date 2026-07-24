"""Generic LLM node — calls the model with bound tools and system prompt."""

from __future__ import annotations

from openai import APIError as OpenAIAPIError

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from ai.models.config import AgentConfig
from ai.state import AgentState
from ai.tool_protocol import ToolProtocol
from ai.logger import get_logger

logger = get_logger(__name__)

MEMORY_PREAMBLE = """\n\n## Conversation Memory

The following is a summary of our conversation so far. Use it to
remember what the user has already asked and what you have found.

{summary}"""

_FALLBACK_CONTENT = (
    "I encountered an issue while processing your request. "
    "Please try rephrasing your question or ask me to perform a simpler action."
)


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

    # Build system prompt — append conversation summary if available
    system_content = prompt
    summary = state.get("summary")
    if summary:
        system_content += MEMORY_PREAMBLE.format(summary=summary)

    messages = [SystemMessage(content=system_content), *state["messages"]]

    # Pass runnable_config so LangGraph's streaming callbacks are attached.
    # Without this, stream_mode="messages" yields the whole response as one chunk.
    try:
        logger.info("Calling LLM", model=config.model)
        
        # Disable parallel tool calls to prevent excessive duplicate tool executions
        bound_model = model.bind_tools(tools, parallel_tool_calls=False)
        response = bound_model.invoke(messages, config=runnable_config)
        
        logger.info("LLM responded")
        return {"messages": [response]}
    except OpenAIAPIError as exc:
        # The LLM server rejected a function call (e.g. malformed args or
        # incompatible schema). Return a fallback message so the stream
        # doesn't crash — the agent will recover on the next iteration.
        error_detail = getattr(exc, "message", str(exc))
        logger.warning(
            "LLM API error (likely rejected tool call)", error=error_detail)
        return {
            "messages": [
                AIMessage(
                    content=(
                        f"{_FALLBACK_CONTENT}\n\n"
                        f"(Internal note: tool call failed — {error_detail})"
                    )
                )
            ]
        }
    except Exception as exc:
        logger.error("Unexpected error during LLM call", error=str(exc))
        raise
