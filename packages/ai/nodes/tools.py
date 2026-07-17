"""Generic tools node — wraps any list of tools into a ToolNode."""

from __future__ import annotations

import functools
from langgraph.prebuilt import ToolNode

from ai.tool_protocol import ToolProtocol
from ai.logger import get_logger

logger = get_logger(__name__)


def make_tools_node(tools: list[ToolProtocol]) -> ToolNode:
    """Wrap a list of ToolProtocol objects into a LangGraph ToolNode.

    The tools are converted to LangChain-compatible format using
    their ``name``, ``description``, ``args_schema``, and ``execute``.
    """
    for tool in tools:
        if hasattr(tool, "_run"):
            original_run = tool._run

            @functools.wraps(original_run)
            def safe_run(*args, _tool_name=tool.name, _orig=original_run, **kwargs):
                try:
                    return _orig(*args, **kwargs)
                except Exception as e:
                    logger.error("Tool execution failed", tool=_tool_name, error=str(e), exc_info=True)
                    return f"Error executing tool '{_tool_name}': {str(e)}"

            # We must assign the wrapper without binding it with __get__ since _run is usually unbound or accessed directly
            tool._run = safe_run

        if hasattr(tool, "_arun"):
            original_arun = tool._arun

            @functools.wraps(original_arun)
            async def safe_arun(*args, _tool_name=tool.name, _orig=original_arun, **kwargs):
                try:
                    return await _orig(*args, **kwargs)
                except Exception as e:
                    logger.error("Tool execution failed", tool=_tool_name, error=str(e), exc_info=True)
                    return f"Error executing tool '{_tool_name}': {str(e)}"

            tool._arun = safe_arun

    return ToolNode(tools)

