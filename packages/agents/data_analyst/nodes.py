"""Graph node implementations for Data Analyst agent."""

from __future__ import annotations

import functools
from openai import APIError as OpenAIAPIError

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from .config import DataAnalystConfig
from .logger import get_logger
from .state import DataAnalystState

logger = get_logger(__name__)

MEMORY_PREAMBLE = """\n\n## Conversation Memory

The following is a summary of our conversation so far. Use it to
remember what the user has already asked and what you have found.

{summary}"""

_FALLBACK_CONTENT = (
    "I encountered an issue while processing your request. "
    "Please try rephrasing your question or ask me to perform a simpler action."
)

SUMMARY_PROMPT = """You are a memory manager. Your job is to maintain a concise
running summary of the conversation so far.

Rules:
1. Preserve key facts: dataset paths, column names, statistics, findings.
2. Preserve user goals and preferences.
3. Keep the summary under 500 characters.
4. If the previous summary already covers the conversation, return it unchanged.
5. Only add new information from the latest exchange.

Previous summary: {summary}

Latest exchange:
User: {user_message}
Assistant: {assistant_message}

Updated summary:"""


def make_llm_node(
    state: DataAnalystState,
    config: DataAnalystConfig,
    tools: list,
    prompt: str,
    *,
    runnable_config: RunnableConfig | None = None,
) -> dict:
    """Build and invoke the LLM with the current state."""
    model = ChatOpenAI(
        model=config.model,
        base_url=config.base_url,
        api_key=config.api_key or "placeholder-key",
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    system_content = prompt
    summary = state.get("summary")
    if summary:
        system_content += MEMORY_PREAMBLE.format(summary=summary)

    messages = [SystemMessage(content=system_content), *state["messages"]]

    try:
        logger.info("Calling LLM", model=config.model)
        bound_model = model.bind_tools(tools, parallel_tool_calls=False)
        response = bound_model.invoke(messages, config=runnable_config)
        logger.info("LLM responded")
        return {"messages": [response]}
    except OpenAIAPIError as exc:
        error_detail = getattr(exc, "message", str(exc))
        logger.warning("LLM API error (likely rejected tool call)", error=error_detail)
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


def make_tools_node(tools: list) -> ToolNode:
    """Wrap tools into a LangGraph ToolNode with exception safety."""
    for tool in tools:
        if hasattr(tool, "_run"):
            original_run = tool._run

            @functools.wraps(original_run)
            def safe_run(*args, _tool_name=getattr(tool, "name", "tool"), _orig=original_run, **kwargs):
                try:
                    return _orig(*args, **kwargs)
                except Exception as e:
                    logger.error("Tool execution failed", tool=_tool_name, error=str(e), exc_info=True)
                    return f"Error executing tool '{_tool_name}': {str(e)}"

            tool._run = safe_run

        if hasattr(tool, "_arun"):
            original_arun = tool._arun

            @functools.wraps(original_arun)
            async def safe_arun(*args, _tool_name=getattr(tool, "name", "tool"), _orig=original_arun, **kwargs):
                try:
                    return await _orig(*args, **kwargs)
                except Exception as e:
                    logger.error("Tool execution failed", tool=_tool_name, error=str(e), exc_info=True)
                    return f"Error executing tool '{_tool_name}': {str(e)}"

            tool._arun = safe_arun

    return ToolNode(tools)


def make_summary_node(config: DataAnalystConfig) -> callable:
    """Build the summary-update node."""
    model = ChatOpenAI(
        model=config.model,
        base_url=config.base_url,
        api_key=config.api_key or "placeholder-key",
        temperature=0,
    )

    def summarize(state: DataAnalystState) -> dict:
        last_user = None
        last_ai = None
        for msg in reversed(state["messages"]):
            if msg.type == "human" and last_user is None:
                last_user = msg.content
            elif msg.type == "ai" and last_ai is None:
                last_ai = msg.content
            if last_user is not None and last_ai is not None:
                break

        if last_user is None or last_ai is None:
            return {"summary": state.get("summary", "")}

        prompt = SUMMARY_PROMPT.format(
            summary=state.get("summary", ""),
            user_message=str(last_user)[:2000],
            assistant_message=str(last_ai)[:2000],
        )

        logger.info("Generating conversation summary")
        new_summary = model.invoke([HumanMessage(content=prompt)]).content
        logger.info("Conversation summary updated", length=len(new_summary))
        return {"summary": new_summary.strip()}

    return summarize
