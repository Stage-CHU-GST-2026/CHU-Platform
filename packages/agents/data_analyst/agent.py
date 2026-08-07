"""Data Analyst Agent class and factory."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.base import BaseStore

from .config import DEFAULT_PROMPT, DEFAULT_YAML, DataAnalystConfig, load_agent_config, load_prompt
from .graph import build_data_analyst_graph
from .logger import get_logger
from .state import DataAnalystState
from .tools import DATA_ANALYST_TOOLS

logger = get_logger(__name__)


class DataAnalystAgent:
    """Data Analyst AI Agent."""

    def __init__(
        self,
        config: DataAnalystConfig,
        tools: list,
        prompt: str = "You are a helpful data analyst.",
        checkpointer: InMemorySaver | None = None,
        store: BaseStore | None = None,
    ) -> None:
        self.config = config
        self.tools = tools
        self.prompt = prompt
        self.checkpointer = checkpointer or InMemorySaver()
        self.graph = build_data_analyst_graph(
            config=config,
            tools=tools,
            prompt=prompt,
            checkpointer=self.checkpointer,
            store=store,
        )

    async def run(
        self,
        message: str,
        config: RunnableConfig | None = None,
    ) -> Any:
        """Send a message to the agent and return the final response."""
        state: DataAnalystState = {
            "messages": [HumanMessage(content=message)],
            "summary": "",
        }
        if config is None:
            config = {"configurable": {"thread_id": str(uuid4())}}
        elif "configurable" not in config or "thread_id" not in config["configurable"]:
            config.setdefault("configurable", {})
            config["configurable"].setdefault("thread_id", str(uuid4()))

        thread_id = config["configurable"]["thread_id"]
        logger.info("Starting agent run", thread_id=thread_id)

        try:
            result = await self.graph.ainvoke(state, config=config)
            logger.info("Agent run completed", thread_id=thread_id)
            return result["messages"][-1]
        except Exception as e:
            logger.error("Agent run failed", thread_id=thread_id, error=str(e), exc_info=True)
            raise

    async def astream(
        self,
        message: str,
        config: RunnableConfig | None = None,
    ):
        """Stream the agent's response token by token."""
        state: DataAnalystState = {
            "messages": [HumanMessage(content=message)],
            "summary": "",
        }
        if config is None:
            config = {"configurable": {"thread_id": str(uuid4())}}
        elif "configurable" not in config or "thread_id" not in config["configurable"]:
            config.setdefault("configurable", {})
            config["configurable"].setdefault("thread_id", str(uuid4()))

        thread_id = config["configurable"]["thread_id"]
        logger.info("Starting agent stream", thread_id=thread_id)

        try:
            async for chunk, _metadata in self.graph.astream(
                state,
                stream_mode="messages",
                config=config,
            ):
                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    yield chunk.content
            logger.info("Agent stream completed", thread_id=thread_id)
        except Exception as e:
            logger.error("Agent stream failed", thread_id=thread_id, error=str(e), exc_info=True)
            raise

    async def get_memory(
        self,
        thread_id: str,
    ) -> str:
        """Inspect the agent's conversation summary for a given thread."""
        state = await self.graph.aget_state(
            {"configurable": {"thread_id": thread_id}},
        )
        if state is not None and state.values.get("summary"):
            return state.values["summary"]
        return ""

    async def get_full_state(
        self,
        thread_id: str,
    ) -> dict | None:
        """Inspect the agent's full state for a given thread."""
        state = await self.graph.aget_state(
            {"configurable": {"thread_id": thread_id}},
        )
        if state is not None:
            return dict(state.values)
        return None


# Backward compatibility alias
Agent = DataAnalystAgent


def create_data_analyst(
    config: DataAnalystConfig | None = None,
    checkpointer: InMemorySaver | None = None,
    store: BaseStore | None = None,
) -> DataAnalystAgent:
    """Create a Data Analyst agent from configuration."""
    cfg = config or load_agent_config(DEFAULT_YAML)
    prompt = load_prompt(DEFAULT_PROMPT)

    return DataAnalystAgent(
        config=cfg,
        tools=DATA_ANALYST_TOOLS,
        prompt=prompt,
        checkpointer=checkpointer,
        store=store,
    )
