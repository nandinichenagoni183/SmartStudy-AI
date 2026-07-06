import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "smartstudy.db")

def get_connection():
    """Create and return a database connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Student Profile
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subjects TEXT NOT NULL,          -- Comma-separated subjects
        exam_date TEXT NOT NULL,         -- YYYY-MM-DD
        daily_hours REAL NOT NULL,
        weak_subjects TEXT NOT NULL,     -- Comma-separated weak subjects
        analysis_report TEXT,            -- Recommendations from Study Analysis Agent
        updated_at TEXT NOT NULL
    )
    """)
    
    # 2. Calendar Events (Study slots, Mock tests, Breaks)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        event_date TEXT NOT NULL,        -- YYYY-MM-DD
        start_time TEXT NOT NULL,        -- HH:MM
        end_time TEXT NOT NULL,          -- HH:MM
        subject TEXT,
        category TEXT DEFAULT 'Study',    -- 'Study', 'Revision', 'Break', 'Mock Test'
        is_completed INTEGER DEFAULT 0
    )
    """)
    
    # 3. Reminders (Spaced Repetition & Mock Alerts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        reminder_date TEXT NOT NULL,     -- YYYY-MM-DD
        reminder_time TEXT DEFAULT '09:00', -- HH:MM
        is_dismissed INTEGER DEFAULT 0,
        ref_table TEXT,                  -- Reference table (e.g., 'calendar_events' or 'tasks')
        ref_id INTEGER
    )
    """)
    
    # 4. Task Manager (To-dos)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        subject TEXT,
        due_date TEXT NOT NULL,          -- YYYY-MM-DD
        status TEXT DEFAULT 'Pending',   -- 'Pending', 'In Progress', 'Completed'
        priority TEXT DEFAULT 'Medium',  -- 'High', 'Medium', 'Low'
        created_at TEXT NOT NULL
    )
    """)
    
    # 5. Study Notes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        subject TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # 6. Progress Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS progress_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date TEXT UNIQUE NOT NULL,   -- YYYY-MM-DD
        hours_studied REAL DEFAULT 0.0,
        tasks_completed INTEGER DEFAULT 0,
        notes_written INTEGER DEFAULT 0,
        revision_completed INTEGER DEFAULT 0
    )
    """)
    
    conn.commit()
    conn.close()

def seed_sample_data():
    """Seed the database with sample data for demonstrating features immediately."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if student profile exists, if yes, don't re-seed
    cursor.execute("SELECT COUNT(*) FROM student_profile")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_str = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    two_days_ago_str = (now - timedelta(days=2)).strftime("%Y-%m-%d")
    three_days_ago_str = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    exam_str = (now + timedelta(days=45)).strftime("%Y-%m-%d")

    # 1. Profile Seed
    cursor.execute("""
    INSERT INTO student_profile (name, subjects, exam_date, daily_hours, weak_subjects, analysis_report, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Alex Mercer",
        "Mathematics, Physics, Computer Science, English Literature",
        exam_str,
        4.5,
        "Physics, Mathematics",
        "## Personalized Learning Plan Summary\n- **Target Exam Date**: " + exam_str + "\n- **Primary Strategy**: Distribute daily 4.5 hours with a 2:1 ratio focusing on weak subjects (Physics and Math) during peak morning hours. Use Spaced Repetition for English Literature formulas and syntax definitions.\n- **Recommendations**: Focus on mechanics and calculus in week 1. Run practice mock tests every alternate Sunday.",
        today_str
    ))
    
    # 2. Tasks Seed
    tasks = [
        ("Solve Physics Mechanics worksheet", "Complete chapter 3 exercises on dynamics", "Physics", today_str, "Pending", "High"),
        ("Read English Literature Act II", "Summarize character motivations in Macbeth", "English Literature", tomorrow_str, "Pending", "Low"),
        ("Code binary search tree", "Implement deletion algorithm in Python", "Computer Science", yesterday_str, "Completed", "Medium"),
        ("Revise calculus limits", "Solve 10 limit calculation problems", "Mathematics", two_days_ago_str, "Completed", "High"),
        ("Physics mock test preparation", "Formulas sheet for electrostatics", "Physics", three_days_ago_str, "Completed", "High")
    ]
    for title, desc, subj, due, status, prio in tasks:
        cursor.execute("""
        INSERT INTO tasks (title, description, subject, due_date, status, priority, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, desc, subj, due, status, prio, today_str))

    # 3. Calendar Events Seed (Today and Tomorrow)
    events = [
        ("Math: Limits & Continuity", "Study formulas and complete limits problems", today_str, "09:00", "10:30", "Mathematics", "Study", 1),
        ("Physics: Dynamics & Kinematics", "Focus on free-body diagrams", today_str, "11:00", "12:30", "Physics", "Study", 0),
        ("Break: Pomodoro Walk", "Stretch and hydrate", today_str, "12:30", "12:50", None, "Break", 1),
        ("Computer Science: Tree Algorithms", "Implement binary search deletion", today_str, "14:00", "15:30", "Computer Science", "Study", 0),
        ("Revision: Literature Terms", "Flashcards on Shakespeare terms", tomorrow_str, "10:00", "11:00", "English Literature", "Revision", 0),
        ("Physics mock exam", "Timed paper from 2024 syllabus", tomorrow_str, "13:00", "16:00", "Physics", "Mock Test", 0)
    ]
    for title, desc, ev_date, start, end, subj, cat, comp in events:
        cursor.execute("""
        INSERT INTO calendar_events (title, description, event_date, start_time, end_time, subject, category, is_completed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, desc, ev_date, start, end, subj, cat, comp))

    # 4. Reminders Seed
    reminders = [
        ("Review Physics mechanics equations (Spaced Repetition: Day 3)", today_str, "08:30", 0, "calendar_events", 2),
        ("Prepare workspace for Physics Mock Exam tomorrow", today_str, "18:00", 0, "calendar_events", 6),
        ("Math limits formulas check (Spaced Repetition: Day 1)", tomorrow_str, "09:00", 0, None, None)
    ]
    for msg, r_date, r_time, dis, ref_t, ref_id in reminders:
        cursor.execute("""
        INSERT INTO reminders (message, reminder_date, reminder_time, is_dismissed, ref_table, ref_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (msg, r_date, r_time, dis, ref_t, ref_id))

    # 5. Notes Seed
    notes = [
        ("Limits & Derivatives Core Formulas", "## Limits\n- $\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1$\n- $\\lim_{x \\to 0} (1+x)^{1/x} = e$\n\n## Derivative Rules\n- Product: $(uv)' = u'v + uv'$\n- Quotient: $(\\frac{u}{v})' = \\frac{u'v - uv'}{v^2}$", "Mathematics", today_str),
        ("Physics: Newton's Laws & Friction", "## Newton's Second Law\n$F_{net} = m \\cdot a$\n\n## Friction Force\n$f_s \\le \\mu_s N$\n$f_k = \\mu_k N$\nwhere $N$ is the normal force.", "Physics", yesterday_str)
    ]
    for title, content, subj, cr_at in notes:
        cursor.execute("""
        INSERT INTO notes (title, content, subject, created_at)
        VALUES (?, ?, ?, ?)
        """, (title, content, subj, cr_at))

    # 6. Progress Logs Seed (Past 4 Days)
    progress = [
        (three_days_ago_str, 3.5, 1, 0, 0),
        (two_days_ago_str, 4.0, 1, 0, 1),
        (yesterday_str, 4.8, 1, 1, 0),
        (today_str, 1.5, 0, 1, 0) # Studied 1.5h so far today
    ]
    for log_date, hrs, tasks_c, notes_w, rev_c in progress:
        cursor.execute("""
        INSERT INTO progress_logs (log_date, hours_studied, tasks_completed, notes_written, revision_completed)
        VALUES (?, ?, ?, ?, ?)
        """, (log_date, hrs, tasks_c, notes_w, rev_c))

    conn.commit()
    conn.close()

# Database Helper Functions

def get_student_profile():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_profile ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_student_profile(name, subjects, exam_date, daily_hours, weak_subjects, analysis_report=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM student_profile ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if row:
        cursor.execute("""
        UPDATE student_profile 
        SET name=?, subjects=?, exam_date=?, daily_hours=?, weak_subjects=?, analysis_report=COALESCE(?, analysis_report), updated_at=?
        WHERE id=?
        """, (name, subjects, exam_date, daily_hours, weak_subjects, analysis_report, now_str, row['id']))
    else:
        cursor.execute("""
        INSERT INTO student_profile (name, subjects, exam_date, daily_hours, weak_subjects, analysis_report, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, subjects, exam_date, daily_hours, weak_subjects, analysis_report, now_str))
    conn.commit()
    conn.close()
    return True

# Calendar Helpers
def add_calendar_event_db(title, description, event_date, start_time, end_time, subject=None, category='Study'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO calendar_events (title, description, event_date, start_time, end_time, subject, category)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, description, event_date, start_time, end_time, subject, category))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return event_id

def list_calendar_events_db(start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM calendar_events"
    params = []
    if start_date and end_date:
        query += " WHERE event_date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE event_date >= ?"
        params.append(start_date)
    elif end_date:
        query += " WHERE event_date <= ?"
        params.append(end_date)
    query += " ORDER BY event_date ASC, start_time ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_event_status_db(event_id, is_completed):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE calendar_events SET is_completed=? WHERE id=?", (is_completed, event_id))
    conn.commit()
    conn.close()
    return True

def delete_calendar_event_db(event_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calendar_events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()
    return True

# Tasks Helpers
def add_task_db(title, description, subject, due_date, priority='Medium'):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO tasks (title, description, subject, due_date, status, priority, created_at)
    VALUES (?, ?, ?, ?, 'Pending', ?, ?)
    """, (title, description, subject, due_date, priority, now_str))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def list_tasks_db(status=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM tasks"
    params = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " ORDER BY due_date ASC, case priority when 'High' then 1 when 'Medium' then 2 else 3 end"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_task_status_db(task_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
    
    # If completed, let's update progress log for today
    if status == 'Completed':
        today_str = datetime.now().strftime("%Y-%m-%d")
        # Ensure log exists
        cursor.execute("INSERT OR IGNORE INTO progress_logs (log_date) VALUES (?)", (today_str,))
        cursor.execute("UPDATE progress_logs SET tasks_completed = tasks_completed + 1 WHERE log_date=?", (today_str,))
        
    conn.commit()
    conn.close()
    return True

def delete_task_db(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return True

# Notes Helpers
def add_note_db(title, content, subject):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO notes (title, content, subject, created_at)
    VALUES (?, ?, ?, ?)
    """, (title, content, subject, now_str))
    
    # Update progress log for today
    cursor.execute("INSERT OR IGNORE INTO progress_logs (log_date) VALUES (?)", (now_str,))
    cursor.execute("UPDATE progress_logs SET notes_written = notes_written + 1 WHERE log_date=?", (now_str,))
    
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id

def list_notes_db(subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM notes"
    params = []
    if subject:
        query += " WHERE subject = ?"
        params.append(subject)
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_note_by_id_db(note_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id=?", (note_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_note_db(note_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
    return True

# Reminders Helpers
def add_reminder_db(message, reminder_date, reminder_time='09:00', ref_table=None, ref_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO reminders (message, reminder_date, reminder_time, is_dismissed, ref_table, ref_id)
    VALUES (?, ?, ?, 0, ?, ?)
    """, (message, reminder_date, reminder_time, ref_table, ref_id))
    conn.commit()
    reminder_id = cursor.lastrowid
    conn.close()
    return reminder_id

def list_reminders_db(is_dismissed=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders WHERE is_dismissed=? ORDER BY reminder_date ASC, reminder_time ASC", (is_dismissed,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def dismiss_reminder_db(reminder_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reminders SET is_dismissed=1 WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()
    return True

# Progress Log Helpers
def log_study_hours_db(hours):
    conn = get_connection()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT OR IGNORE INTO progress_logs (log_date) VALUES (?)", (today_str,))
    cursor.execute("UPDATE progress_logs SET hours_studied = hours_studied + ? WHERE log_date=?", (hours, today_str))
    conn.commit()
    conn.close()
    return True

def get_progress_logs_db(limit=7):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress_logs ORDER BY log_date DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in reversed(rows)]

def get_streak_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT log_date FROM progress_logs WHERE hours_studied > 0 ORDER BY log_date DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return 0
        
    streak = 0
    today = datetime.now().date()
    current_check = today
    
    # Convert rows to date objects
    dates = {datetime.strptime(row['log_date'], "%Y-%m-%d").date() for row in rows}
    
    # Check if today is in dates or yesterday is in dates (streak is active)
    if today not in dates and (today - timedelta(days=1)) not in dates:
        return 0
        
    if today not in dates:
        current_check = today - timedelta(days=1)
        
    while current_check in dates:
        streak += 1
        current_check -= timedelta(days=1)
        
    return streak

def clear_database():
    """Clear all records from database tables for debugging or resetting."""
    conn = get_connection()
    cursor = conn.cursor()
    tables = ['student_profile', 'calendar_events', 'reminders', 'tasks', 'notes', 'progress_logs']
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.close()
    init_db()
    seed_sample_data()
    return True
