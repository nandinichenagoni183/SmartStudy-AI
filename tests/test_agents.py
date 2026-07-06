import os
import sys

# Adjust path to import from local src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, seed_sample_data, get_student_profile
from src.agents.study_analysis_agent import get_study_analysis_agent
from src.agents.timetable_agent import get_timetable_agent
from src.agents.revision_agent import get_revision_agent
from src.agents.progress_tracking_agent import get_progress_tracking_agent
from src.agents.motivation_agent import get_motivation_agent
from src.agents.doubt_solver_agent import get_doubt_solver_agent
from src.agents.orchestrator import run_agent, setup_api_keys

def test_agents():
    print("Starting Google ADK Multi-Agent Validation Tests...")
    
    # 1. Initialize DB for agent tools
    init_db()
    seed_sample_data()
    
    # 2. Setup API key and check if available
    api_key = setup_api_keys()
    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable not set. Running agents in mock/dry-run mode.")
    else:
        print("Gemini API key configured successfully.")

    # 3. Instantiate all agents
    print("Instantiating agents...")
    agents = {
        "StudyAnalysisAgent": get_study_analysis_agent(),
        "TimetableAgent": get_timetable_agent(),
        "RevisionAgent": get_revision_agent(),
        "ProgressTrackingAgent": get_progress_tracking_agent(),
        "MotivationAgent": get_motivation_agent(),
        "AIDoubtSolverAgent": get_doubt_solver_agent()
    }
    
    # 4. Verify properties
    for name, agent in agents.items():
        if hasattr(agent, "name") and agent.name:
            print(f"Agent successfully registered: {agent.name}")
            print(f"  - Model: {getattr(agent, 'model', 'default')}")
            print(f"  - Tools: {[t.__name__ for t in getattr(agent, 'tools', [])]}")
        else:
            print(f"Error: Agent '{name}' is not fully functional.")
            return False
            
    # 5. Run a brief dry run test if API key is present
    if api_key:
        print("Running actual API test with Motivation Agent...")
        try:
            response = run_agent(
                agents["MotivationAgent"],
                "Please generate a 2-sentence motivational quote and tip for a student studying Computer Science.",
                session_id="test_motivate_session"
            )
            print("\nAgent Response:")
            print("-" * 50)
            print(response)
            print("-" * 50)
            print("Agent API Call: PASSED")
        except Exception as e:
            print(f"Error executing Agent API call: {str(e)}")
            print("Note: If the error is due to an invalid Gemini API Key, configure a valid key.")
            return False
    else:
        print("Skipping actual API check because no API key was provided. Configure GEMINI_API_KEY to test model responses.")
        
    print("Google ADK Agents validation completed successfully! All checks PASSED.")
    return True

if __name__ == "__main__":
    success = test_agents()
    sys.exit(0 if success else 1)
