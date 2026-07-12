from ai.agent import Agent
from ai.models.config import AgentConfig
from ai.tool_protocol import ToolProtocol


def create_agent(
    config: AgentConfig | None = None,
    tools: list[ToolProtocol] | None = None,
    prompt: str = "You are a helpful assistant.",
) -> Agent:
    """Create a generic Agent with optional config, tools, and prompt."""
    return Agent(
        config=config or AgentConfig(),
        tools=tools or [],
        prompt=prompt,
    )
