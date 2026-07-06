from src.agents.orchestrator import Agent, STUDY_PLANNING_TOOLS

def get_study_analysis_agent():
    """
    Returns the Study Analysis Agent.
    This agent analyzes student inputs and constructs a tailored learning strategy.
    """
    return Agent(
        name="StudyAnalysisAgent",
        model="gemini-2.5-flash",
        description="Analyzes the student's academic profile and recommends high-level strategies.",
        instruction=(
            "You are the Study Analysis Agent for SmartStudy AI.\n\n"
            "Your role is to collect and analyze the student's academic profile:\n"
            "1. Student Name\n"
            "2. Subjects being studied\n"
            "3. Target Exam Date\n"
            "4. Daily study hours target\n"
            "5. Weak subjects\n\n"
            "Task instructions:\n"
            "- Perform a strategic needs analysis.\n"
            "- Recommend how to distribute daily study hours. Standard practice: Allocate 60% of daily time to weak subjects during peak energy periods, and 40% to stronger subjects.\n"
            "- Outline week-by-week checkpoints leading up to the exam.\n"
            "- Output your evaluation in a clear, beautiful Markdown report with headers, bullet points, and highlight blocks (e.g., target milestones).\n"
            "- Provide encouragement and structured study methods (e.g., Active Recall, Spaced Repetition).\n"
            "- If requested, save details using the notes tool or tasks tool."
        ),
        tools=STUDY_PLANNING_TOOLS
    )
