import streamlit as st
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

# Adjust path to import from local src directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import (
    init_db, seed_sample_data, get_student_profile, update_student_profile,
    add_task_db, list_tasks_db, update_task_status_db, delete_task_db,
    add_calendar_event_db, list_calendar_events_db, delete_calendar_event_db, update_event_status_db,
    add_note_db, list_notes_db, get_note_by_id_db, delete_note_db,
    add_reminder_db, list_reminders_db, dismiss_reminder_db,
    log_study_hours_db, get_progress_logs_db, get_streak_db, clear_database
)

from src.mcp_client import test_mcp_connection

from src.agents.study_analysis_agent import get_study_analysis_agent
from src.agents.timetable_agent import get_timetable_agent
from src.agents.revision_agent import get_revision_agent
from src.agents.progress_tracking_agent import get_progress_tracking_agent
from src.agents.motivation_agent import get_motivation_agent
from src.agents.doubt_solver_agent import get_doubt_solver_agent
from src.agents.orchestrator import run_agent, setup_api_keys

# Set up Streamlit Page Configuration
st.set_page_config(
    page_title="SmartStudy AI – Multi-Agent Study Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #151030 100%);
        color: #f1f5f9;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Titles and Headers */
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.025em;
    }
    
    .main-title {
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Interactive Card container */
    .card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.25);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .card:hover {
        border-color: rgba(129, 140, 248, 0.3);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #818cf8;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa 0%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Spaced Repetition Tags */
    .spaced-tag {
        background: rgba(244, 114, 182, 0.15);
        color: #f472b6;
        border: 1px solid rgba(244, 114, 182, 0.3);
        border-radius: 6px;
        padding: 0.2rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Task Completed Checkbox Style */
    .task-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .task-row:last-child {
        border-bottom: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()
seed_sample_data()

# Handle Session State Variables
if 'gemini_key' not in st.session_state:
    st.session_state.gemini_key = os.environ.get("GEMINI_API_KEY", "")
    
if st.session_state.gemini_key:
    os.environ["GEMINI_API_KEY"] = st.session_state.gemini_key
    os.environ["GOOGLE_API_KEY"] = st.session_state.gemini_key

# Page Title
st.markdown("<div class='main-title'>SmartStudy AI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Multi-Agent Study Planner & Productivity Assistant</div>", unsafe_allow_html=True)

# Fetch Current Profile
profile = get_student_profile()

if not profile:
    st.warning("⚠️ No student profile found! Please configure your study profile in the **Study Planner** tab first.")

# Navigation Tabs
tabs = st.tabs([
    "🏠 Dashboard", 
    "📝 Study Planner", 
    "📅 Timetable", 
    "🔄 Revision Planner", 
    "📊 Progress Tracker", 
    "💬 AI Chat Assistant", 
    "⚙️ Settings"
])

# =====================================================================
# TAB 1: DASHBOARD
# =====================================================================
with tabs[0]:
    if profile:
        col1, col2, col3, col4 = st.columns(4)
        
        # Calculate Streak
        streak = get_streak_db()
        # Today's Studied Hours
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_log = [log for log in get_progress_logs_db(1) if log['log_date'] == today_str]
        today_hours = today_log[0]['hours_studied'] if today_log else 0.0
        # Pending Tasks
        pending_tasks = len(list_tasks_db("Pending"))
        # Upcoming Events
        upcoming_events = len(list_calendar_events_db(start_date=today_str))

        with col1:
            st.markdown(f"""
            <div class='card'>
                <div class='metric-label'>Study Streak</div>
                <div class='metric-value'>🔥 {streak} Days</div>
                <div style='font-size:0.8rem; color:#94a3b8; margin-top:0.4rem;'>Keep consistency active!</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class='card'>
                <div class='metric-label'>Hours Logged Today</div>
                <div class='metric-value'>⏱️ {today_hours:.1f} / {profile['daily_hours']:.1f} hr</div>
                <div style='font-size:0.8rem; color:#94a3b8; margin-top:0.4rem;'>Daily study hours target</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class='card'>
                <div class='metric-label'>Pending Tasks</div>
                <div class='metric-value'>📋 {pending_tasks} Tasks</div>
                <div style='font-size:0.8rem; color:#94a3b8; margin-top:0.4rem;'>Check progress checklist</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            st.markdown(f"""
            <div class='card'>
                <div class='metric-label'>Upcoming Events</div>
                <div class='metric-value'>📅 {upcoming_events} Items</div>
                <div style='font-size:0.8rem; color:#94a3b8; margin-top:0.4rem;'>Scheduled study slots</div>
            </div>
            """, unsafe_allow_html=True)

        # Dashboard body layout
        body_col1, body_col2 = st.columns([2, 1])
        
        with body_col1:
            # 1. Today's Timetable
            st.markdown("<h3 style='color:#818cf8; margin-bottom:1rem;'>📅 Today's Study Slots</h3>", unsafe_allow_html=True)
            today_events = list_calendar_events_db(start_date=today_str, end_date=today_str)
            if today_events:
                for ev in today_events:
                    comp_status = "✅ Completed" if ev['is_completed'] else "⏳ Pending"
                    badge_color = "rgba(16, 185, 129, 0.15)" if ev['is_completed'] else "rgba(245, 158, 11, 0.15)"
                    text_color = "#10b981" if ev['is_completed'] else "#f59e0b"
                    
                    st.markdown(f"""
                    <div style='background:rgba(30, 41, 59, 0.3); border:1px solid rgba(255, 255, 255, 0.05); border-radius:10px; padding:0.8rem; margin-bottom:0.6rem; display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <span style='font-weight:600; font-size:1.05rem; color:#f8fafc;'>{ev['title']}</span>
                            <span style='margin-left:0.5rem; font-size:0.75rem; background:rgba(99, 102, 241, 0.15); color:#818cf8; border:1px solid rgba(99, 102, 241, 0.3); border-radius:4px; padding:0.1rem 0.4rem;'>{ev['subject'] or 'General'}</span>
                            <div style='font-size:0.8rem; color:#94a3b8; margin-top:0.2rem;'>⏱️ {ev['start_time']} - {ev['end_time']} | {ev['description'] or ''}</div>
                        </div>
                        <div style='background:{badge_color}; color:{text_color}; font-size:0.8rem; font-weight:600; padding:0.2rem 0.6rem; border-radius:6px;'>
                            {comp_status}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No study sessions scheduled for today yet. Use the **Timetable** tab to generate study slots.")

            # 2. Spaced Repetition Alerts
            st.markdown("<h3 style='color:#f472b6; margin-top:1.5rem; margin-bottom:1rem;'>🔔 Active Reminders & Alerts</h3>", unsafe_allow_html=True)
            reminders = list_reminders_db(is_dismissed=0)
            if reminders:
                for rem in reminders:
                    col_rem_text, col_rem_btn = st.columns([5, 1])
                    with col_rem_text:
                        st.markdown(f"""
                        <div style='background:rgba(244, 114, 182, 0.08); border:1px solid rgba(244, 114, 182, 0.2); border-radius:10px; padding:0.8rem; margin-bottom:0.6rem;'>
                            <div style='font-weight:600; color:#f472b6;'>🔔 {rem['message']}</div>
                            <div style='font-size:0.8rem; color:#94a3b8; margin-top:0.2rem;'>Scheduled for: {rem['reminder_date']} at {rem['reminder_time']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_rem_btn:
                        st.write("") # spacing
                        if st.button("Dismiss", key=f"dismiss_{rem['id']}"):
                            dismiss_reminder_db(rem['id'])
                            st.rerun()
            else:
                st.success("You are all caught up! No pending review reminders.")

        with body_col2:
            # 3. Motivation Widget
            st.markdown("<h3 style='color:#c084fc; margin-bottom:1rem;'>💡 Mindset & Motivation</h3>", unsafe_allow_html=True)
            
            # Simple offline fallback quote generator if API fails
            sample_quotes = [
                ("The secret of getting ahead is getting started.", "Mark Twain"),
                ("It always seems impossible until it's done.", "Nelson Mandela"),
                ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
                ("Focus on progress, not perfection.", "Bill Gates")
            ]
            import random
            q_text, q_author = random.choice(sample_quotes)
            
            st.markdown(f"""
            <div class='card' style='background:rgba(192, 132, 252, 0.08); border-color:rgba(192, 132, 252, 0.2);'>
                <div style='font-style:italic; font-size:1.1rem; color:#e2e8f0; margin-bottom:0.8rem;'>"{q_text}"</div>
                <div style='text-align:right; font-weight:600; color:#c084fc; font-size:0.9rem;'>— {q_author}</div>
            </div>
            """, unsafe_allow_html=True)

            # Generate fresh quote using Motivation Agent
            if st.button("Request Fresh AI Tip"):
                if not st.session_state.gemini_key:
                    st.error("Please add your Gemini API Key in Settings to use the AI Motivation Agent.")
                else:
                    with st.spinner("Calling Motivation Agent..."):
                        mot_agent = get_motivation_agent()
                        prompt = f"The student is currently studying: {profile['subjects']}. Their weak subjects are {profile['weak_subjects']}. Write a short pep talk and study technique."
                        mot_resp = run_agent(mot_agent, prompt)
                        st.markdown(f"""
                        <div class='card' style='background:rgba(192, 132, 252, 0.12); border-color:#c084fc;'>
                            <div class='card-header'>✨ AI Pep Talk</div>
                            <div style='font-size:0.9rem; line-height:1.5;'>{mot_resp}</div>
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.info("Welcome to SmartStudy AI! Get started by setting up your study profile in the **Study Planner** tab.")

# =====================================================================
# TAB 2: STUDY PLANNER
# =====================================================================
with tabs[1]:
    st.header("📝 Create Your Personalized Study Profile")
    st.write("Setting up your study configuration allows our agents to craft customized schedules and target strategies.")

    # Profile Setup Form
    with st.form("profile_form"):
        col_name, col_hours = st.columns(2)
        with col_name:
            student_name = st.text_input("Full Name", value=profile['name'] if profile else "Alex Mercer")
        with col_hours:
            daily_hours = st.number_input("Target Study Hours Per Day", min_value=1.0, max_value=15.0, value=profile['daily_hours'] if profile else 4.0, step=0.5)
            
        col_subjects, col_weak = st.columns(2)
        with col_subjects:
            subjects = st.text_input("Subjects (comma-separated)", value=profile['subjects'] if profile else "Mathematics, Physics, Computer Science, English Literature")
        with col_weak:
            weak_subjects = st.text_input("Weak Subjects / Focus Areas (comma-separated)", value=profile['weak_subjects'] if profile else "Physics, Mathematics")
            
        exam_date = st.date_input("Target Exam Date", value=datetime.strptime(profile['exam_date'], "%Y-%m-%d") if profile else (datetime.now() + timedelta(days=30)))
        
        submit_profile = st.form_submit_button("💾 Save Study Profile")
        
    if submit_profile:
        # Simple Validation
        if not student_name.strip() or not subjects.strip() or not weak_subjects.strip():
            st.error("Please fill in all profile fields. Inputs must not be empty.")
        else:
            # Check if exam date is in future
            if exam_date < datetime.now().date():
                st.warning("Warning: Selected exam date is in the past!")
            update_student_profile(
                student_name,
                subjects,
                exam_date.strftime("%Y-%m-%d"),
                daily_hours,
                weak_subjects
            )
            st.success("Success! Study profile updated. Re-run analysis below to refresh details.")
            st.rerun()

    # Agent Study Analysis Section
    if profile:
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("🕵️ AI Study Analysis & Strategy Guide")
        
        if profile['analysis_report']:
            st.markdown(profile['analysis_report'])
        else:
            st.info("No analysis report generated yet. Click the button below to have the Study Analysis Agent formulate your strategy.")
            
        if st.button("🔍 Generate AI Strategic Study Plan"):
            if not st.session_state.gemini_key:
                st.error("Please add your Gemini API Key in Settings to run the Study Analysis Agent.")
            else:
                with st.spinner("Study Analysis Agent is evaluating your needs..."):
                    analysis_agent = get_study_analysis_agent()
                    prompt = (
                        f"Student Profile:\n"
                        f"- Name: {profile['name']}\n"
                        f"- Subjects: {profile['subjects']}\n"
                        f"- Weak Subjects: {profile['weak_subjects']}\n"
                        f"- Daily Target Hours: {profile['daily_hours']}\n"
                        f"- Exam Date: {profile['exam_date']}\n\n"
                        f"Please generate a complete study analysis and strategy. Save a summary in notes if helpful."
                    )
                    report = run_agent(analysis_agent, prompt)
                    
                    # Save generated report back to profile DB
                    update_student_profile(
                        profile['name'], profile['subjects'], profile['exam_date'],
                        profile['daily_hours'], profile['weak_subjects'], report
                    )
                    st.success("Successfully generated strategy report!")
                    st.rerun()

# =====================================================================
# TAB 3: TIMETABLE
# =====================================================================
with tabs[2]:
    st.header("📅 Weekly Study Timetable")
    st.write("Track and schedule daily study blocks. Red and yellow highlight weak subjects, green schedules breaks, and indigo represents study blocks.")
    
    if profile:
        # Load Weekly events
        start_week = datetime.now().strftime("%Y-%m-%d")
        end_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        events = list_calendar_events_db()
        
        col_tbl_actions, col_tbl_spacer = st.columns([1, 2])
        with col_tbl_actions:
            if st.button("🤖 Generate 3-Day Balanced Timetable with AI"):
                if not st.session_state.gemini_key:
                    st.error("Please add your Gemini API Key in Settings to run the Timetable Agent.")
                else:
                    with st.spinner("Timetable Agent is balancing subjects and scheduling blocks..."):
                        timetable_agent = get_timetable_agent()
                        prompt = (
                            f"Generate study slots for the next 3 days starting today ({start_week}).\n"
                            f"Student Info:\n"
                            f"- Subjects: {profile['subjects']}\n"
                            f"- Weak Focus Subjects: {profile['weak_subjects']}\n"
                            f"- Daily Limit: {profile['daily_hours']} hours.\n\n"
                            f"Call the 'mcp_add_calendar_event' tool to insert each study/break slot into the calendar. Balance weak subjects with easy ones, and include Pomodoro breaks."
                        )
                        agent_summary = run_agent(timetable_agent, prompt)
                        st.success("Timetable generated and saved to DB successfully!")
                        st.markdown(agent_summary)
                        st.rerun()

        # Manual Timetable Session Creation Form
        st.markdown("<br/>", unsafe_allow_html=True)
        with st.expander("➕ Add Study Session Manually", expanded=False):
            with st.form("manual_session_form"):
                col_sub, col_top = st.columns(2)
                with col_sub:
                    manual_subject = st.text_input("Subject (e.g. Mathematics, Physics)")
                with col_top:
                    manual_topic = st.text_input("Topic / Session Title")
                
                col_date, col_start, col_end, col_cat = st.columns(4)
                with col_date:
                    manual_date = st.date_input("Date", value=datetime.now().date())
                with col_start:
                    manual_start = st.time_input("Start Time", value=datetime.now().time())
                with col_end:
                    default_end = (datetime.combine(datetime.today(), datetime.now().time()) + timedelta(hours=1)).time()
                    manual_end = st.time_input("End Time", value=default_end)
                with col_cat:
                    manual_category = st.selectbox(
                        "Category", 
                        ["Study", "Revision", "Break", "Mock Test", "Assignment"]
                    )
                
                add_session_submitted = st.form_submit_button("Add Session")
                
            if add_session_submitted:
                if not manual_topic.strip():
                    st.error("Topic / Session Title cannot be empty.")
                elif manual_end <= manual_start:
                    st.error("End Time must be after Start Time.")
                else:
                    date_str = manual_date.strftime("%Y-%m-%d")
                    start_str = manual_start.strftime("%H:%M")
                    end_str = manual_end.strftime("%H:%M")
                    
                    add_calendar_event_db(
                        title=manual_topic,
                        description=f"Manual study session for {manual_topic}",
                        event_date=date_str,
                        start_time=start_str,
                        end_time=end_str,
                        subject=manual_subject.strip() if manual_subject.strip() else None,
                        category=manual_category
                    )
                    st.success("Session added successfully!")
                    st.rerun()

        # Display Schedule in Table
        if events:
            df = pd.DataFrame(events)
            # Reorder and filter columns for clean UI
            df_display = df[['event_date', 'start_time', 'end_time', 'title', 'subject', 'category', 'is_completed', 'id']]
            df_display.columns = ['Date', 'Start Time', 'End Time', 'Session Title', 'Subject', 'Category', 'Completed', 'Event ID']
            
            # Interactive Completion Update
            st.markdown("<br/>", unsafe_allow_html=True)
            for idx, row in df_display.iterrows():
                col_info, col_checkbox, col_delete = st.columns([5, 1, 1])
                with col_info:
                    cat_color = "#818cf8"
                    if row['Category'] == 'Break': cat_color = "#34d399"
                    elif row['Category'] == 'Mock Test': cat_color = "#f472b6"
                    elif row['Category'] == 'Assignment': cat_color = "#a78bfa"
                    elif row['Subject'] in [s.strip() for s in profile['weak_subjects'].split(',')]: cat_color = "#fbbf24"
                    
                    st.markdown(f"""
                    <div style='background:rgba(30, 41, 59, 0.2); border-left: 4px solid {cat_color}; padding: 0.6rem 1rem; border-radius: 6px; margin-bottom: 0.5rem;'>
                        <strong>{row['Session Title']}</strong> | {row['Date']} ({row['Start Time']} - {row['End Time']})
                        <br/><span style='font-size:0.8rem; color:#94a3b8;'>Subject: {row['Subject'] or 'General'} | Category: {row['Category']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_checkbox:
                    is_completed = st.checkbox("Done", value=bool(row['Completed']), key=f"ev_check_{row['Event ID']}")
                    if is_completed != bool(row['Completed']):
                        update_event_status_db(row['Event ID'], int(is_completed))
                        st.rerun()
                with col_delete:
                    if st.button("🗑️ Delete", key=f"ev_del_{row['Event ID']}"):
                        delete_calendar_event_db(row['Event ID'])
                        st.rerun()
        else:
            st.info("Your calendar is empty for the next 7 days. Press the button above to have AI populate it.")
    else:
        st.warning("Define your profile in Study Planner to generate timetables.")

# =====================================================================
# TAB 4: REVISION PLANNER
# =====================================================================
with tabs[3]:
    st.header("🔄 Spaced Repetition Revision Scheduler")
    st.write("Spaced repetition helps you review topics at increasing intervals (Day 1, 3, 7, 14, 30) for maximum retention.")

    if profile:
        col_rev_form, col_rev_info = st.columns([2, 1])
        
        with col_rev_form:
            st.subheader("📚 Add New Revision Topic")
            with st.form("revision_topic_form"):
                topic_title = st.text_input("Topic Name (e.g. Newton's 2nd Law, Organic Chemistry intro)")
                topic_subject = st.selectbox("Subject", [s.strip() for s in profile['subjects'].split(',')])
                start_date = st.date_input("Start Revision From", value=datetime.now().date())
                
                submit_rev = st.form_submit_button("🤖 Generate Spaced Repetition Schedule")
                
            if submit_rev:
                if not topic_title.strip():
                    st.error("Topic name cannot be empty.")
                elif not st.session_state.gemini_key:
                    st.error("Please add your Gemini API Key in Settings to run the Revision Agent.")
                else:
                    with st.spinner("Revision Agent is creating schedules..."):
                        revision_agent = get_revision_agent()
                        prompt = (
                            f"Create a spaced repetition review schedule for:\n"
                            f"- Topic: {topic_title}\n"
                            f"- Subject: {topic_subject}\n"
                            f"- Start Date: {start_date.strftime('%Y-%m-%d')}\n\n"
                            f"Please register the reviews using 'mcp_add_calendar_event' and set reminders with 'mcp_add_reminder'. Add a mock test task with high priority."
                        )
                        response = run_agent(revision_agent, prompt)
                        st.success("Revision schedule created and registered successfully!")
                        st.markdown(response)
                        
        with col_rev_info:
            st.subheader("ℹ️ Spaced Repetition Science")
            st.markdown("""
            Memory decay happens rapidly after learning something new. Reviewing topics at specific intervals resets the decay curve:
            - **Review 1**: 24 Hours later (Day 1)
            - **Review 2**: 3 Days later (Day 3)
            - **Review 3**: 7 Days later (Day 7)
            - **Review 4**: 14 Days later (Day 14)
            - **Review 5**: 30 Days later (Day 30)
            
            The Revision Agent automatically schedules these sessions into your calendar and sets dashboard notifications to remind you.
            """)
            
        # Display Scheduled Revision Sessions
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("🗓️ Scheduled Revision Sessions")
        events = list_calendar_events_db()
        revision_events = [e for e in events if e['category'] == 'Revision' or e['category'] == 'Mock Test']
        
        if revision_events:
            for re in revision_events:
                status_color = "#f472b6" if re['category'] == 'Mock Test' else "#c084fc"
                status_icon = "📝" if re['category'] == 'Mock Test' else "🔄"
                
                st.markdown(f"""
                <div style='background:rgba(30, 41, 59, 0.2); border:1px solid rgba(255, 255, 255, 0.05); border-radius:10px; padding:0.8rem; margin-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <span style='font-size:1.1rem;'>{status_icon} <strong>{re['title']}</strong></span>
                        <span style='margin-left:0.5rem; font-size:0.75rem; background:rgba(192, 132, 252, 0.15); color:#c084fc; border:1px solid rgba(192, 132, 252, 0.3); border-radius:4px; padding:0.1rem 0.4rem;'>{re['subject']}</span>
                        <div style='font-size:0.8rem; color:#94a3b8; margin-top:0.2rem;'>Date: {re['event_date']} | Time: {re['start_time']} - {re['end_time']}</div>
                    </div>
                    <div>
                        <span style='font-size:0.8rem; font-weight:600; padding:0.2rem 0.6rem; border-radius:6px; background:rgba(255, 255, 255, 0.05); color:#94a3b8;'>{re['category']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No spaced repetition revisions scheduled yet. Add a topic above to generate a schedule.")
    else:
        st.warning("Define your profile in Study Planner to generate revision plans.")

# =====================================================================
# TAB 5: PROGRESS TRACKER
# =====================================================================
with tabs[4]:
    st.header("📊 Progress & Performance Dashboard")

    if profile:
        col_track_left, col_track_right = st.columns([1, 1])
        
        with col_track_left:
            # 1. Log Study Hours
            st.subheader("⏱️ Log Hours Studied Today")
            with st.form("log_hours_form"):
                hours_input = st.number_input("Hours Spent Studying", min_value=0.5, max_value=24.0, value=1.0, step=0.5)
                submit_hours = st.form_submit_button("✅ Log Hours")
                
            if submit_hours:
                log_study_hours_db(hours_input)
                st.success(f"Logged {hours_input} study hours successfully for today!")
                st.rerun()

            # 2. Add custom task
            st.subheader("➕ Add Study Task")
            with st.form("add_task_form"):
                t_title = st.text_input("Task Title")
                t_desc = st.text_area("Task Description")
                t_sub = st.selectbox("Subject", [s.strip() for s in profile['subjects'].split(',')])
                t_date = st.date_input("Due Date")
                t_prio = st.selectbox("Priority", ["High", "Medium", "Low"])
                submit_task = st.form_submit_button("Create Task")
                
            if submit_task:
                if not t_title.strip():
                    st.error("Task title cannot be empty.")
                else:
                    add_task_db(t_title, t_desc, t_sub, t_date.strftime("%Y-%m-%d"), t_prio)
                    st.success("Task added to checklist!")
                    st.rerun()

        with col_track_right:
            # 3. Tasks Checklist
            st.subheader("📋 Study Tasks Checklist")
            tasks = list_tasks_db()
            if tasks:
                for t in tasks:
                    col_t_info, col_t_check, col_t_del = st.columns([4, 1, 1])
                    with col_t_info:
                        strike_start = "~~" if t['status'] == "Completed" else ""
                        strike_end = "~~" if t['status'] == "Completed" else ""
                        prio_color = "#ef4444" if t['priority'] == "High" else ("#fbbf24" if t['priority'] == "Medium" else "#60a5fa")
                        
                        st.markdown(f"""
                        <div style='background:rgba(255, 255, 255, 0.02); border-left:3px solid {prio_color}; padding:0.4rem 0.8rem; border-radius:4px; margin-bottom:0.4rem;'>
                            {strike_start}<strong>{t['title']}</strong>{strike_end} 
                            <br/><span style='font-size:0.75rem; color:#94a3b8;'>Due: {t['due_date']} | Subject: {t['subject']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_t_check:
                        is_completed = st.checkbox("Done", value=(t['status'] == "Completed"), key=f"t_check_{t['id']}")
                        if is_completed != (t['status'] == "Completed"):
                            new_status = "Completed" if is_completed else "Pending"
                            update_task_status_db(t['id'], new_status)
                            st.rerun()
                    with col_t_del:
                        if st.button("🗑️", key=f"t_del_{t['id']}"):
                            delete_task_db(t['id'])
                            st.rerun()
            else:
                st.info("Checklist is empty. Add tasks using the form on the left.")

        # Progress Visualizations
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("📈 Performance Visualization")
        
        # Load Logs
        logs = get_progress_logs_db(7)
        if logs:
            df_logs = pd.DataFrame(logs)
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Study Hours Chart
                fig_hours = px.bar(
                    df_logs, x='log_date', y='hours_studied',
                    labels={'log_date': 'Date', 'hours_studied': 'Hours Studied'},
                    title="Daily Study Hours (Last 7 Days)",
                    color_discrete_sequence=['#818cf8']
                )
                fig_hours.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f1f5f9',
                    xaxis_showgrid=False
                )
                st.plotly_chart(fig_hours, use_container_width=True)
                
            with chart_col2:
                # Tasks/Notes completed chart
                fig_tasks = px.line(
                    df_logs, x='log_date', y=['tasks_completed', 'notes_written', 'revision_completed'],
                    labels={'value': 'Count', 'log_date': 'Date', 'variable': 'Activity'},
                    title="Productivity Trend",
                    markers=True
                )
                fig_tasks.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f1f5f9',
                    xaxis_showgrid=False
                )
                st.plotly_chart(fig_tasks, use_container_width=True)
        else:
            st.info("No study history found. Log hours to see charts.")

        # AI Progress Reviewer
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("🔍 Progress Audit & Improvements recommendations")
        
        # Get report
        if st.button("🚀 Run AI Progress Assessment"):
            if not st.session_state.gemini_key:
                st.error("Please add your Gemini API Key in Settings to run the Progress Agent.")
            else:
                with st.spinner("Progress Tracking Agent is analyzing logs..."):
                    tracker_agent = get_progress_tracking_agent()
                    
                    # Construct study logs for prompt
                    db_logs = get_progress_logs_db(7)
                    all_tasks = list_tasks_db()
                    
                    prompt = (
                        f"Student Profile Target: {profile['daily_hours']} hours daily.\n"
                        f"Logged Hours (Last 7 Days): {[{'Date': l['log_date'], 'Hours': l['hours_studied']} for l in db_logs]}\n"
                        f"Checklist Tasks: {[{'Title': t['title'], 'Status': t['status'], 'Priority': t['priority']} for t in all_tasks]}\n\n"
                        f"Evaluate my study metrics and give me a progress report with recommendations on how to organize my study slots next week."
                    )
                    assessment = run_agent(tracker_agent, prompt)
                    st.markdown(f"""
                    <div class='card' style='background:rgba(129, 140, 248, 0.08); border-color:#818cf8;'>
                        <div class='card-header'>🔬 AI Progress Report & Action Items</div>
                        <div style='font-size:0.95rem; line-height:1.6;'>{assessment}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("Define your profile in Study Planner to access progress tracking.")

# =====================================================================
# TAB 6: AI CHAT ASSISTANT
# =====================================================================
with tabs[5]:
    st.header("💬 Multi-Agent Interactive Chat Console")
    st.write("Communicate directly with specialized agents. Use the dropdown to choose your tutor.")

    if profile:
        agent_selection = st.selectbox(
            "Select specialized Agent to consult:",
            ["AI Doubt Solver Agent ( Tutors Core Concepts )", 
             "Motivation Agent ( Boosts focus and routines )", 
             "Study Analysis Agent ( Inspects planning/weakness )", 
             "Timetable Agent ( Reviews schedule generation )"]
        )

        # Map display name to factory function
        agent_mapping = {
            "AI Doubt Solver Agent ( Tutors Core Concepts )": (get_doubt_solver_agent, "doubt_solver"),
            "Motivation Agent ( Boosts focus and routines )": (get_motivation_agent, "motivation"),
            "Study Analysis Agent ( Inspects planning/weakness )": (get_study_analysis_agent, "study_analysis"),
            "Timetable Agent ( Reviews schedule generation )": (get_timetable_agent, "timetable")
        }

        agent_factory, session_key = agent_mapping[agent_selection]

        # Initialize chat histories
        if 'chat_histories' not in st.session_state:
            st.session_state.chat_histories = {}
        if session_key not in st.session_state.chat_histories:
            st.session_state.chat_histories[session_key] = []

        # Display Chat History
        for msg in st.session_state.chat_histories[session_key]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat Input
        if user_prompt := st.chat_input("Ask a question, request a conceptual note, or ask for a study quote:"):
            # Add user message
            st.session_state.chat_histories[session_key].append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)

            # Generate response
            with st.chat_message("assistant"):
                if not st.session_state.gemini_key:
                    st.error("Please add your Gemini API Key in Settings to get responses.")
                else:
                    with st.spinner("Thinking..."):
                        active_agent = agent_factory()
                        
                        # Add profile context to doubt solver
                        if session_key == "doubt_solver":
                            contextual_prompt = (
                                f"[Profile Context: Student is studying {profile['subjects']}. Weak areas are {profile['weak_subjects']}].\n"
                                f"Question: {user_prompt}"
                            )
                        else:
                            contextual_prompt = user_prompt
                            
                        response = run_agent(active_agent, contextual_prompt, session_id=f"chat_{session_key}")
                        st.markdown(response)
                        st.session_state.chat_histories[session_key].append({"role": "assistant", "content": response})
    else:
        st.warning("Define your profile in Study Planner to access chat assistant.")

# =====================================================================
# TAB 7: SETTINGS & DIAGNOSTICS
# =====================================================================
with tabs[6]:
    st.header("⚙️ Configuration & Diagnostics Console")
    st.write("Configure API keys, execute system diagnostic checks, and manage database states.")

    st.subheader("🔑 Gemini API Credentials")
    gemini_key_input = st.text_input("Gemini API Key (saved in local memory)", type="password", value=st.session_state.gemini_key)
    
    if st.button("🔌 Save Credentials & Reconnect"):
        if gemini_key_input.strip():
            st.session_state.gemini_key = gemini_key_input.strip()
            os.environ["GEMINI_API_KEY"] = gemini_key_input.strip()
            os.environ["GOOGLE_API_KEY"] = gemini_key_input.strip()
            st.success("API credentials saved successfully!")
            st.rerun()
        else:
            st.error("API Key cannot be empty.")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("🩺 System Connectivity Diagnostics")
    
    col_diag_mcp, col_diag_gemini = st.columns(2)
    
    with col_diag_mcp:
        st.write("**Model Context Protocol (MCP) Server Status**")
        if st.button("🔍 Check MCP Diagnostics"):
            with st.spinner("Pinging MCP subprocess server..."):
                mcp_ok = test_mcp_connection()
                if mcp_ok:
                    st.success("MCP Connection Diagnostic: PASSED (Tools and Subprocess are fully active)")
                else:
                    st.error("MCP Connection Diagnostic: FAILED. Check if FastMCP or SQLite database is blocked.")
                    
    with col_diag_gemini:
        st.write("**Google Gemini LLM Integration Status**")
        if st.button("⚡ Check Gemini API Diagnostics"):
            if not st.session_state.gemini_key:
                st.error("API Key not found. Please provide a key in the input above first.")
            else:
                with st.spinner("Sending test prompt..."):
                    try:
                        # Instantiate simple test agent
                        test_agent = get_motivation_agent()
                        resp = run_agent(test_agent, "Hello, answer with the word 'Success'.")
                        if "Success" in resp or len(resp) > 0:
                            st.success("Gemini API Diagnostic: PASSED (Successfully generated agent completions)")
                        else:
                            st.error(f"Gemini API Diagnostic: FAILED. Received empty response: {resp}")
                    except Exception as e:
                        st.error(f"Gemini API Diagnostic: FAILED. Error: {str(e)}")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("🧹 System Database Administration")
    st.write("Wipe SQLite databases to clean logs, schedules, and custom settings.")
    
    if st.button("⚠️ Reset Entire Database & Seed Defaults"):
        clear_database()
        st.success("Database has been reset and seeded with default profile details!")
        st.rerun()

    # Display Workspace File Structure
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.subheader("📂 Project Structure Reference")
    st.code("""
SmartStudy_AI/
├── .env.example
├── app.py                     (Streamlit Main Application UI)
├── requirements.txt           (System Dependencies)
├── smartstudy.db              (Shared SQLite Database)
└── src/
    ├── database.py            (SQLite Database Layer & CRUD Helpers)
    ├── mcp_server.py          (FastMCP Server exposing 4 categories of tools)
    ├── mcp_client.py          (MCP stdio subprocess connection client)
    └── agents/
        ├── __init__.py
        ├── orchestrator.py    (Google ADK runner and tool wrappers helper)
        ├── study_analysis_agent.py
        ├── timetable_agent.py
        ├── revision_agent.py
        ├── progress_tracking_agent.py
        ├── motivation_agent.py
        └── doubt_solver_agent.py
    """)
