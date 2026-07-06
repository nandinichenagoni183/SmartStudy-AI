import os
from google import genai
from google.genai import types

# Import Agent and tools directly from orchestrator to avoid Google ADK dependency
import src.agents.orchestrator
from src.agents.orchestrator import Agent, STUDY_PLANNING_TOOLS

def get_timetable_agent():
    """
    Returns the Timetable Agent.
    This agent generates balanced timetables.
    """
    return Agent(
        name="TimetableAgent",
        model="gemini-2.5-flash",
        description="Generates optimized study timetables and balances difficult and easy subjects.",
        instruction=(
            "You are the Timetable Agent for SmartStudy AI.\n\n"
            "Your role is to generate personalized daily and weekly study timetables:\n"
            "- Balance difficult/weak subjects (e.g. Mathematics, Physics) with easier/stronger subjects (e.g. English, Computer Science).\n"
            "- Schedule study sessions in 'Pomodoro blocks' (e.g., 50 minutes of focused study, followed by a 10-minute break, or 25/5 blocks).\n"
            "- Output a complete weekly study timetable in a beautiful Markdown table format."
        ),
        tools=STUDY_PLANNING_TOOLS
    )

# Save the original run_agent function
original_run_agent = src.agents.orchestrator.run_agent

def patched_run_agent(agent, prompt, session_id="default_session", user_id="default_user"):
    """
    Monkey-patched run_agent to intercept TimetableAgent execution.
    Uses only google-genai Client and generate_content directly as required.
    """
    agent_name = getattr(agent, "name", "")
    if agent_name == "TimetableAgent":
        src.agents.orchestrator.setup_api_keys()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "The agent did not yield a text response. Please check your Gemini API key."
        
        # Instantiate a fresh Client for every request as required
        client = genai.Client(api_key=api_key)
        
        system_instruction = getattr(agent, "instruction", "")
        config = types.GenerateContentConfig(
            system_instruction=system_instruction if system_instruction else None
        )
        
        # Enforce generating a complete weekly timetable in markdown format
        enhanced_prompt = (
            prompt + 
            "\n\nIMPORTANT: Ignore tools and generate a complete weekly timetable in markdown format."
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=enhanced_prompt,
            config=config
        )
        
        if response.text:
            return response.text
        return "The agent did not yield a text response."
    else:
        return original_run_agent(agent, prompt, session_id, user_id)

# Apply monkey patch
src.agents.orchestrator.run_agent = patched_run_agent
