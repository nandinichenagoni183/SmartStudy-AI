import os
import sys
import traceback
from google import genai
from google.genai import types

class Agent:
    """Mock Agent class to store agent configuration for google-genai runtime."""
    def __init__(self, name: str, model: str, description: str = "", instruction: str = "", tools: list = None, **kwargs):
        self.name = name
        self.model = model
        self.description = description
        self.instruction = instruction
        self.tools = tools or []

# Adjust sys.path to allow imports from local src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp_client import call_mcp_tool

# Ensure API Key Synchronization
def setup_api_keys():
    """Ensure both standard API key names are set for Gemini."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        os.environ["GEMINI_API_KEY"] = api_key
    return api_key

# =====================================================================
# WRAPPER TOOLS FOR GOOGLE GENAI AGENTS
# =====================================================================

def mcp_add_calendar_event(title: str, description: str, event_date: str, start_time: str, end_time: str, subject: str = None, category: str = 'Study') -> str:
    """
    Add a study event, exam, break, or mock test to the calendar.
    event_date: YYYY-MM-DD, start_time/end_time: HH:MM, category: 'Study', 'Revision', 'Break', 'Mock Test'.
    """
    res = call_mcp_tool("add_calendar_event", {
        "title": title, "description": description, "event_date": event_date,
        "start_time": start_time, "end_time": end_time, "subject": subject, "category": category
    })
    return str(res)

def mcp_list_calendar_events(start_date: str = None, end_date: str = None) -> str:
    """List calendar events in YYYY-MM-DD range."""
    res = call_mcp_tool("list_calendar_events", {"start_date": start_date, "end_date": end_date})
    return str(res)

def mcp_add_reminder(message: str, reminder_date: str, reminder_time: str = '09:00') -> str:
    """Add a revision or mock reminder on a specific date (YYYY-MM-DD) and time (HH:MM)."""
    res = call_mcp_tool("add_reminder", {"message": message, "reminder_date": reminder_date, "reminder_time": reminder_time})
    return str(res)

def mcp_add_task(title: str, description: str, subject: str, due_date: str, priority: str = 'Medium') -> str:
    """Add a study task. due_date: YYYY-MM-DD, priority: 'High', 'Medium', 'Low'."""
    res = call_mcp_tool("add_task", {"title": title, "description": description, "subject": subject, "due_date": due_date, "priority": priority})
    return str(res)

def mcp_list_tasks(status: str = None) -> str:
    """List study tasks. status: 'Pending', 'In Progress', 'Completed'."""
    res = call_mcp_tool("list_tasks", {"status": status})
    return str(res)

def mcp_update_task_status(task_id: int, status: str) -> str:
    """Update task status. status: 'Pending', 'In Progress', 'Completed'."""
    res = call_mcp_tool("update_task_status", {"task_id": task_id, "status": status})
    return str(res)

def mcp_add_note(title: str, content: str, subject: str) -> str:
    """Save custom notes or learning summaries under a subject. content can be Markdown."""
    res = call_mcp_tool("add_note", {"title": title, "content": content, "subject": subject})
    return str(res)

def mcp_list_notes(subject: str = None) -> str:
    """List all notes or filter by subject."""
    res = call_mcp_tool("list_notes", {"subject": subject})
    return str(res)

# Standard set of tools for agents
STUDY_PLANNING_TOOLS = [
    mcp_add_calendar_event, mcp_list_calendar_events,
    mcp_add_reminder,
    mcp_add_task, mcp_list_tasks, mcp_update_task_status,
    mcp_add_note, mcp_list_notes
]

# =====================================================================
# INITIALIZE AND EXECUTE AGENTS
# =====================================================================

# Global dictionary to persist chat history across invocations.
# Key format: (user_id, session_id, agent_name) -> list of types.Content objects
_session_histories = {}

def run_agent(agent: Agent, prompt: str,
              session_id: str = "default_session",
              user_id: str = "default_user") -> str:
    """
    Synchronous execution of a google-genai agent.
    Maintains session history in memory by passing the history list to a new
    chat instance created from a fresh genai.Client on every call.
    """
    setup_api_keys()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "The agent did not yield a text response. Please check your Gemini API key."

    try:
        # Use duck typing to handle both mock Agent and real ADK Agent
        agent_name = getattr(agent, "name", "Agent")
        model_name = getattr(agent, "model", "gemini-2.5-flash")
        instruction = getattr(agent, "instruction", getattr(agent, "instructions", ""))
        tools = getattr(agent, "tools", [])

        # Create client for this request
        client = genai.Client(api_key=api_key)

        key = (user_id, session_id, agent_name)
        history = _session_histories.get(key, [])

        config = types.GenerateContentConfig(
            system_instruction=instruction if instruction else None,
            tools=tools if tools else None
        )

        chat = client.chats.create(
            model=model_name,
            config=config,
            history=history
        )

        response = chat.send_message(prompt)

        # Persist the chat history for future invocations
        _session_histories[key] = chat.get_history()

        if response.text:
            return response.text
        return "The agent did not yield a text response."

    except Exception:
        return traceback.format_exc()
