from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

from ai.graph import build_graph
from ai.models.config import AgentConfig
from ai.state import AgentState
from ai.tool_protocol import ToolProtocol


class Agent:
    """Generic AI Agent.

    Knows nothing about CSVs or analysis. It only knows how to:
    - Call an LLM
    - Execute tools
    - Maintain conversation state
    - Run the LangGraph workflow

    Usage:
        agent = Agent(config=agent_config, tools=[...], prompt="You are...")
        result = await agent.run("What's in the data?")
    """

    def __init__(
        self,
        config: AgentConfig,
        tools: list[ToolProtocol],
        prompt: str = "You are a helpful assistant.",
        checkpointer: InMemorySaver | None = None,
    ) -> None:
        self.config = config
        self.tools = tools
        self.prompt = prompt
        self.checkpointer = checkpointer or InMemorySaver()
        self.graph = build_graph(
            config=config,
            tools=tools,
            prompt=prompt,
            checkpointer=self.checkpointer,
        )

    async def run(
        self,
        message: str,
        config: RunnableConfig | None = None,
    ) -> Any:
        """Send a message to the agent and return the final response."""
        state: AgentState = {
            "messages": [HumanMessage(content=message)],
        }
        result = await self.graph.ainvoke(state, config=config)
        return result["messages"][-1]

    async def astream(
        self,
        message: str,
        config: RunnableConfig | None = None,
    ):
        """Stream the agent's response token by token."""
        state: AgentState = {
            "messages": [HumanMessage(content=message)],
        }
        async for chunk, _metadata in self.graph.astream(
            state,
            stream_mode="messages",
            config=config,
        ):
            # Only yield text tokens from the AI model, not tool-result chunks
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield chunk.content
