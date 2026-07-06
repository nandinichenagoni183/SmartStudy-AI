import asyncio
import os
import sys
import json
try:
    import nest_asyncio
    # Only apply nest_asyncio if an event loop is already running
    asyncio.get_running_loop()
    nest_asyncio.apply()
except (RuntimeError, ImportError):
    pass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define the server startup parameters to launch src/mcp_server.py
# Using sys.executable guarantees it uses the same python virtual environment
SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")],
    env=os.environ.copy()
)

def run_async_fn(async_fn, *args, **kwargs):
    """Helper function to run an asynchronous coroutine in the current event loop context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    if loop.is_running():
        return loop.run_until_complete(async_fn(*args, **kwargs))
    else:
        return asyncio.run(async_fn(*args, **kwargs))

async def call_mcp_tool_async(tool_name: str, arguments: dict) -> dict:
    """
    Connects to the MCP server, calls the specified tool with arguments,
    and returns the parsed JSON response.
    """
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as client:
            await client.initialize()
            result = await client.call_tool(tool_name, arguments)
            
            if hasattr(result, "content") and result.content:
                text_content = result.content[0].text
                try:
                    return json.loads(text_content)
                except json.JSONDecodeError:
                    return {"status": "success", "raw_content": text_content}
            return {"status": "error", "message": "No content returned from tool."}

def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """
    Synchronous wrapper to execute an MCP tool. This makes tool usage direct
    and uncomplicated for Streamlit UI actions and Google ADK Agents.
    """
    try:
        return run_async_fn(call_mcp_tool_async, tool_name, arguments)
    except Exception as e:
        return {"status": "error", "message": f"MCP Client connection failed: {str(e)}"}

def test_mcp_connection() -> bool:
    """
    Ping the MCP server by calling list_calendar_events with no args.
    Returns True if connection is successful, False otherwise.
    """
    res = call_mcp_tool("list_calendar_events", {})
    return res.get("status") == "success"
