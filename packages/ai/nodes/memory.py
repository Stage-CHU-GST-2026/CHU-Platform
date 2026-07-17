"""Memory summarization node — maintains a running conversation summary.

After each agent/tool loop, this node uses the LLM to summarize the
conversation so far, preserving key context like dataset paths,
findings, and user preferences across turns.
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from ai.models.config import AgentConfig
from ai.state import AgentState
from ai.logger import get_logger

logger = get_logger(__name__)

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


def make_summary_node(config: AgentConfig) -> callable:
    """Build the summary-update node for the LangGraph.

    This node is called *after* the LLM + tools loop finishes, and
    updates ``state["summary"]`` with a condensed summary of the
    conversation so far.
    """

    model = ChatOpenAI(
        model=config.model,
        base_url=config.base_url,
        api_key=config.api_key or "placeholder-key",
        temperature=0,
    )

    def summarize(state: AgentState) -> dict:
        """Update the conversation summary from the latest messages."""
        # Find the last user message and last AI message
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
        new_summary = model.invoke([SystemMessage(content=prompt)]).content
        logger.info("Conversation summary updated", length=len(new_summary))
        return {"summary": new_summary.strip()}

    return summarize
