import os
import sys

# Adjust path to import from local src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import (
    init_db, seed_sample_data, get_student_profile, update_student_profile,
    add_task_db, list_tasks_db, update_task_status_db,
    add_calendar_event_db, list_calendar_events_db,
    add_note_db, list_notes_db,
    add_reminder_db, list_reminders_db,
    log_study_hours_db, get_progress_logs_db, get_streak_db,
    DB_PATH
)

def test_database():
    print("Starting Database Validation Tests...")
    
    # 1. Initialize and Seed
    print("Initialising database...")
    init_db()
    
    print("Seeding sample data...")
    seed_sample_data()
    
    if os.path.exists(DB_PATH):
        print(f"Database file found at: {DB_PATH}")
    else:
        print("Error: Database file not created.")
        return False

    # 2. Test Profile
    print("Testing Student Profile...")
    profile = get_student_profile()
    if profile:
        print(f"Loaded student profile: {profile['name']}, subjects: {profile['subjects']}")
    else:
        print("Error: Profile not found.")
        return False
        
    update_student_profile("Jane Doe", "Math, Science", "2026-09-01", 5.0, "Science")
    updated_profile = get_student_profile()
    if updated_profile and updated_profile['name'] == "Jane Doe":
        print("Successfully updated student profile.")
    else:
        print("Error: Profile update failed.")
        return False

    # 3. Test Tasks
    print("Testing Tasks CRUD...")
    tasks_before = len(list_tasks_db())
    task_id = add_task_db("Test Task", "Test Description", "Math", "2026-08-01", "High")
    tasks_after = len(list_tasks_db())
    if tasks_after == tasks_before + 1:
        print(f"Successfully added task (ID: {task_id}).")
    else:
        print("Error: Task insertion failed.")
        return False
        
    update_task_status_db(task_id, "Completed")
    completed_task = [t for t in list_tasks_db() if t['id'] == task_id][0]
    if completed_task['status'] == "Completed":
        print("Successfully updated task status.")
    else:
        print("Error: Task status update failed.")
        return False

    # 4. Test Calendar Events
    print("Testing Calendar CRUD...")
    events_before = len(list_calendar_events_db())
    event_id = add_calendar_event_db("Test Session", "Study limit functions", "2026-08-01", "10:00", "11:30", "Math", "Study")
    events_after = len(list_calendar_events_db())
    if events_after == events_before + 1:
        print(f"Successfully added calendar event (ID: {event_id}).")
    else:
        print("Error: Calendar insertion failed.")
        return False

    # 5. Test Notes
    print("Testing Notes CRUD...")
    notes_before = len(list_notes_db())
    note_id = add_note_db("Test Formulas", "E = mc^2", "Physics")
    notes_after = len(list_notes_db())
    if notes_after == notes_before + 1:
        print(f"Successfully added note (ID: {note_id}).")
    else:
        print("Error: Notes insertion failed.")
        return False

    # 6. Test Reminders
    print("Testing Reminders...")
    rem_id = add_reminder_db("Check calculus notes", "2026-08-01", "08:00")
    reminders = list_reminders_db()
    if len(reminders) > 0:
        print(f"Successfully added reminder (ID: {rem_id}).")
    else:
        print("Error: Reminder listing failed.")
        return False

    # 7. Test Progress and Streak
    print("Testing Progress Tracking...")
    log_study_hours_db(2.5)
    logs = get_progress_logs_db(1)
    if len(logs) > 0:
        print(f"Logged study hours verified: {logs[0]['hours_studied']} hrs.")
    else:
        print("Error: Progress logging failed.")
        return False
        
    streak = get_streak_db()
    print(f"Current study streak: {streak} days.")
    
    print("Database validation completed successfully! All database checks PASSED.")
    return True

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
