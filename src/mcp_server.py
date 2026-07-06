import os
import sys
import json
from datetime import datetime

# Adjust path to import from local src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from src.database import (
    add_calendar_event_db, list_calendar_events_db, delete_calendar_event_db, update_event_status_db,
    add_reminder_db, list_reminders_db, dismiss_reminder_db,
    add_task_db, list_tasks_db, update_task_status_db, delete_task_db,
    add_note_db, list_notes_db, get_note_by_id_db, delete_note_db
)

# Create the MCP Server
mcp = FastMCP("SmartStudy_MCP_Server")

# =====================================================================
# CALENDAR TOOLS
# =====================================================================

@mcp.tool()
def add_calendar_event(title: str, description: str, event_date: str, start_time: str, end_time: str, subject: str = None, category: str = 'Study') -> str:
    """
    Add a new study session, exam, break, or mock test to the calendar.
    
    Args:
        title: Title of the event (e.g. "Physics Mechanics Study").
        description: Details about the study goals or topics to cover.
        event_date: Date in YYYY-MM-DD format.
        start_time: Start time in HH:MM format (24-hour).
        end_time: End time in HH:MM format (24-hour).
        subject: The academic subject associated with this study session.
        category: Category of event: 'Study', 'Revision', 'Break', or 'Mock Test'.
    """
    try:
        # Input validation
        datetime.strptime(event_date, "%Y-%m-%d")
        datetime.strptime(start_time, "%H:%M")
        datetime.strptime(end_time, "%H:%M")
        
        event_id = add_calendar_event_db(title, description, event_date, start_time, end_time, subject, category)
        return json.dumps({
            "status": "success",
            "message": f"Successfully scheduled {category} event '{title}'",
            "event_id": event_id,
            "details": {
                "title": title,
                "date": event_date,
                "time": f"{start_time}-{end_time}",
                "subject": subject,
                "category": category
            }
        })
    except ValueError as ve:
        return json.dumps({"status": "error", "message": f"Invalid date or time format. Date must be YYYY-MM-DD, times must be HH:MM. Error: {str(ve)}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to add calendar event: {str(e)}"})

@mcp.tool()
def list_calendar_events(start_date: str = None, end_date: str = None) -> str:
    """
    List scheduled events from the study calendar, optionally filtered by a date range.
    
    Args:
        start_date: Optional start date (YYYY-MM-DD).
        end_date: Optional end date (YYYY-MM-DD).
    """
    try:
        events = list_calendar_events_db(start_date, end_date)
        return json.dumps({"status": "success", "events": events})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to list calendar events: {str(e)}"})

@mcp.tool()
def update_calendar_event_status(event_id: int, is_completed: bool) -> str:
    """
    Mark a calendar study slot as completed or incomplete.
    
    Args:
        event_id: The ID of the event to update.
        is_completed: True to mark completed, False otherwise.
    """
    try:
        status = 1 if is_completed else 0
        update_event_status_db(event_id, status)
        return json.dumps({"status": "success", "message": f"Event {event_id} completion status updated to {is_completed}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def delete_calendar_event(event_id: int) -> str:
    """
    Remove an event from the study calendar.
    
    Args:
        event_id: The unique ID of the event to delete.
    """
    try:
        delete_calendar_event_db(event_id)
        return json.dumps({"status": "success", "message": f"Successfully deleted calendar event with ID {event_id}."})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to delete event: {str(e)}"})

# =====================================================================
# REMINDER TOOLS
# =====================================================================

@mcp.tool()
def add_reminder(message: str, reminder_date: str, reminder_time: str = '09:00', ref_table: str = None, ref_id: int = None) -> str:
    """
    Set an automated revision or study alert reminder.
    
    Args:
        message: The reminder text (e.g. "Spaced Repetition: Physics Day 7 Review").
        reminder_date: Date in YYYY-MM-DD format.
        reminder_time: Time of day in HH:MM format.
        ref_table: Optional table to reference (e.g., 'tasks').
        ref_id: Optional ID of the referenced item.
    """
    try:
        datetime.strptime(reminder_date, "%Y-%m-%d")
        datetime.strptime(reminder_time, "%H:%M")
        
        rem_id = add_reminder_db(message, reminder_date, reminder_time, ref_table, ref_id)
        return json.dumps({
            "status": "success",
            "message": f"Reminder set: '{message}' on {reminder_date} at {reminder_time}",
            "reminder_id": rem_id
        })
    except ValueError as ve:
        return json.dumps({"status": "error", "message": f"Invalid date/time format: {str(ve)}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to set reminder: {str(e)}"})

@mcp.tool()
def list_reminders(include_dismissed: bool = False) -> str:
    """
    List all pending alerts and reminders.
    
    Args:
        include_dismissed: If True, returns both active and dismissed reminders.
    """
    try:
        reminders = list_reminders_db(is_dismissed=(1 if include_dismissed else 0))
        return json.dumps({"status": "success", "reminders": reminders})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def dismiss_reminder(reminder_id: int) -> str:
    """
    Acknowledge and dismiss an active reminder.
    
    Args:
        reminder_id: The ID of the reminder to dismiss.
    """
    try:
        dismiss_reminder_db(reminder_id)
        return json.dumps({"status": "success", "message": f"Reminder {reminder_id} dismissed successfully."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

# =====================================================================
# TASK MANAGER TOOLS
# =====================================================================

@mcp.tool()
def add_task(title: str, description: str, subject: str, due_date: str, priority: str = 'Medium') -> str:
    """
    Add a task to the checklist (e.g., homework, chapter readings, exercises).
    
    Args:
        title: Brief name of the task.
        description: In-depth details or steps.
        subject: The specific study subject.
        due_date: Target completion date in YYYY-MM-DD.
        priority: Priority level: 'High', 'Medium', or 'Low'.
    """
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
        if priority not in ('High', 'Medium', 'Low'):
            priority = 'Medium'
            
        task_id = add_task_db(title, description, subject, due_date, priority)
        return json.dumps({
            "status": "success",
            "message": f"Task '{title}' created successfully",
            "task_id": task_id
        })
    except ValueError as ve:
        return json.dumps({"status": "error", "message": f"Invalid due_date format: {str(ve)}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def list_tasks(status: str = None) -> str:
    """
    Fetch study tasks from the tracker.
    
    Args:
        status: Optional filter by status: 'Pending', 'In Progress', 'Completed'.
    """
    try:
        tasks = list_tasks_db(status)
        return json.dumps({"status": "success", "tasks": tasks})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def update_task_status(task_id: int, status: str) -> str:
    """
    Update the status of a specific task.
    
    Args:
        task_id: The ID of the task.
        status: New status: 'Pending', 'In Progress', or 'Completed'.
    """
    try:
        if status not in ('Pending', 'In Progress', 'Completed'):
            return json.dumps({"status": "error", "message": "Status must be 'Pending', 'In Progress', or 'Completed'"})
            
        update_task_status_db(task_id, status)
        return json.dumps({"status": "success", "message": f"Task {task_id} status updated to {status}."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def delete_task(task_id: int) -> str:
    """
    Remove a task from the list.
    
    Args:
        task_id: The ID of the task to delete.
    """
    try:
        delete_task_db(task_id)
        return json.dumps({"status": "success", "message": f"Task {task_id} deleted."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

# =====================================================================
# NOTES TOOLS
# =====================================================================

@mcp.tool()
def add_note(title: str, content: str, subject: str) -> str:
    """
    Save custom notes, learning summaries, formulas sheets, or definitions.
    
    Args:
        title: Title of the note.
        content: Markdown-formatted note content.
        subject: Subject this note belongs to.
    """
    try:
        note_id = add_note_db(title, content, subject)
        return json.dumps({
            "status": "success",
            "message": f"Note '{title}' saved successfully under subject '{subject}'",
            "note_id": note_id
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def list_notes(subject: str = None) -> str:
    """
    Fetch saved study notes, optionally filtered by subject.
    
    Args:
        subject: Optional academic subject filter.
    """
    try:
        notes = list_notes_db(subject)
        return json.dumps({"status": "success", "notes": notes})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def get_note(note_id: int) -> str:
    """
    Retrieve details and full markdown content of a specific note.
    
    Args:
        note_id: Unique note ID.
    """
    try:
        note = get_note_by_id_db(note_id)
        if note:
            return json.dumps({"status": "success", "note": note})
        return json.dumps({"status": "error", "message": f"Note with ID {note_id} not found."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@mcp.tool()
def delete_note(note_id: int) -> str:
    """
    Delete a saved note.
    
    Args:
        note_id: ID of the note to remove.
    """
    try:
        delete_note_db(note_id)
        return json.dumps({"status": "success", "message": f"Note {note_id} deleted successfully."})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

if __name__ == "__main__":
    # Start the FastMCP stdio server
    mcp.run()
