"""Generic tools node — wraps any list of tools into a ToolNode."""

from __future__ import annotations

from langgraph.prebuilt import ToolNode

from ai.tool_protocol import ToolProtocol


def make_tools_node(tools: list[ToolProtocol]) -> ToolNode:
    """Wrap a list of ToolProtocol objects into a LangGraph ToolNode.

    The tools are converted to LangChain-compatible format using
    their ``name``, ``description``, ``args_schema``, and ``execute``.
    """
    return ToolNode(tools)
