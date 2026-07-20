"""Generic AI framework.

Knows nothing about CSVs, datasets, or analysis.
Only knows how to call an LLM, execute tools, and maintain a conversation.
"""

from .agent import Agent

__all__ = [
    "Agent",
]
