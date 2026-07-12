"""Protocol/interface for tools that can be used by the AI framework."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ToolProtocol(Protocol):
    """A tool that the AI framework can execute.

    Every tool must provide:
    - name: Unique identifier for the LLM to reference
    - description: What the tool does (used by the LLM to decide when to call it)
    - args_schema: JSON schema or Pydantic model for the tool's arguments
    - execute(): Async method that runs the tool's logic
    """

    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    @property
    def args_schema(self) -> type | dict[str, Any] | None: ...

    async def execute(self, **kwargs: Any) -> Any: ...
