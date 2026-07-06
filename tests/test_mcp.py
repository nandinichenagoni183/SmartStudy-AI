import os
import sys

# Adjust path to import from local src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp_client import call_mcp_tool, test_mcp_connection
from src.database import init_db

def test_mcp():
    print("Starting Model Context Protocol (MCP) Validation Tests...")
    
    # Ensure database is initialised first
    init_db()
    
    # 1. Ping the server
    print("Pinging MCP Server via Stdio Transport...")
    is_connected = test_mcp_connection()
    if is_connected:
        print("MCP Connection check: PASSED")
    else:
        print("Error: MCP Connection check failed.")
        return False
        
    # 2. Test Calendar Tool via client
    print("Testing Calendar Tool via MCP Client...")
    res = call_mcp_tool("list_calendar_events", {})
    if res.get("status") == "success":
        print("Successfully listed calendar events via MCP.")
        print(f"Sample Events count: {len(res.get('events', []))}")
    else:
        print(f"Error calling list_calendar_events: {res.get('message')}")
        return False
        
    # 3. Test Task Tool via client
    print("Testing Task Tool via MCP Client...")
    task_res = call_mcp_tool("add_task", {
        "title": "MCP Test Task",
        "description": "Integration test task for model context protocol",
        "subject": "System Engineering",
        "due_date": "2026-08-30",
        "priority": "Low"
    })
    if task_res.get("status") == "success":
        print("Successfully added task via MCP.")
    else:
        print(f"Error calling add_task: {task_res.get('message')}")
        return False

    # 4. Test Notes Tool via client
    print("Testing Notes Tool via MCP Client...")
    note_res = call_mcp_tool("add_note", {
        "title": "MCP Test Note",
        "content": "# MCP Test\nThis note is created through MCP interface.",
        "subject": "System Engineering"
    })
    if note_res.get("status") == "success":
        print("Successfully added note via MCP.")
    else:
        print(f"Error calling add_note: {note_res.get('message')}")
        return False
        
    # Clean up test task and note
    print("Cleaning up test task and note...")
    if "task_id" in task_res:
        call_mcp_tool("delete_task", {"task_id": task_res["task_id"]})
    if "note_id" in note_res:
        call_mcp_tool("delete_note", {"note_id": note_res["note_id"]})

    print("Model Context Protocol (MCP) validation completed successfully! All checks PASSED.")
    return True

if __name__ == "__main__":
    success = test_mcp()
    sys.exit(0 if success else 1)
