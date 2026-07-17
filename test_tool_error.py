import asyncio
from ai.agent import Agent
from ai.models.config import AgentConfig
from langchain.tools import BaseTool

class BadTool(BaseTool):
    name: str = "bad_tool"
    description: str = "always fails"
    def _run(self) -> str:
        raise ValueError("Simulated tool crash")

config = AgentConfig(model="gpt-4o-mini", base_url="https://api.openai.com/v1", api_key="sk-test")
agent = Agent(config=config, tools=[BadTool()])

async def main():
    state = {"messages": []}
    tools_node = agent.graph.nodes["tools"]
    from langchain_core.messages import AIMessage, ToolCall
    msg = AIMessage(content="", tool_calls=[ToolCall(name="bad_tool", args={}, id="call_123")])
    res = tools_node.invoke({"messages": [msg]})
    print("Tool returned:", res)

asyncio.run(main())
