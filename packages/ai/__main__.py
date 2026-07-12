"""
Entry point to run the generic AI agent directly.

Usage:
    python -m packages.ai
"""

import asyncio

from ai import Agent
from ai.models.config import AgentConfig
from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    data = {
        "san francisco": "Foggy, 15°C",
        "new york": "Sunny, 28°C",
        "london": "Rainy, 12°C",
        "tokyo": "Clear, 22°C",
        "paris": "Cloudy, 18°C",
        "sydney": "Sunny, 26°C",
    }
    return f"The weather in {city} is: {data.get(city.lower(), 'unknown')}"


async def main():
    config = AgentConfig()
    agent = Agent(
        config=config,
        tools=[get_weather],
        prompt="You are a helpful weather assistant.",
    )

    print("=" * 60)
    print("Generic AI Agent — Weather Demo")
    print("=" * 60)
    print()

    questions = [
        "What's the weather in San Francisco?",
        "What about Tokyo?",
    ]

    for q in questions:
        print(f"  User: {q}")
        result = await agent.run(q)
        print(f"Agent: {result.content}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
    print()


if __name__ == "__main__":
    asyncio.run(main())
