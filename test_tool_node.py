import asyncio
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage, ToolCall

@tool
def bad_tool(x: int) -> str:
    """A bad tool."""
    raise ValueError("Something went wrong inside the tool!")

async def main():
    tools = [bad_tool]
    node = ToolNode(tools)
    
    msg = AIMessage(content="", tool_calls=[ToolCall(name="bad_tool", args={"x": 1}, id="call_123")])
    try:
        res = node.invoke({"messages": [msg]})
        print("Success:", res)
    except Exception as e:
        print("Crashed:", e)

    # Now with handle_tool_error=True
    bad_tool.handle_tool_error = True
    try:
        res = node.invoke({"messages": [msg]})
        print("With handle_tool_error:", res)
    except Exception as e:
        print("Crashed with handle_tool_error:", e)

asyncio.run(main())
