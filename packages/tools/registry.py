"""Central tool registry — maps names to tool classes."""

from __future__ import annotations

from typing import Any

_TOOLS: dict[str, Any] = {}


def register_tool(tool_class: type) -> type:
    """Register a tool class by its name."""
    instance = tool_class()
    name = instance.name
    _TOOLS[name] = instance
    return tool_class


def get_tool(name: str) -> Any | None:
    """Look up a tool instance by name."""
    return _TOOLS.get(name)


def list_tools() -> dict[str, Any]:
    """Return all registered tools (name → instance)."""
    return dict(_TOOLS)


TOOL_REGISTRY: dict[str, Any] = _TOOLS
