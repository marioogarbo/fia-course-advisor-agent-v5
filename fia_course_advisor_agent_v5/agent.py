from google.adk.agents import Agent
from .tools import send_zoho_email, rag_query
from .prompts import FIA_AGENT_INSTRUCTION, ORCHESTRATOR_AGENT_INSTRUCTION

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Main FIA Course Advisor Agent
fsa_agent = Agent(
    name="fire_safety_assessment_agent",
    model="gemini-2.5-flash",
    description="An agent that advises prospective learners on suitable FIA (Fire Industry Academy) courses based on their job role, fire protection system interests, location, experience, and prior learning.",
    instruction=FIA_AGENT_INSTRUCTION,
    tools=[rag_query, send_zoho_email],
)

orchestrator_agent = Agent(
    name="fia_course_advisor_orchestrator_agent",
    model="gemini-2.5-flash",
    description="Orchestrator agent for FIA Course Advisor system, coordinating workflows and managing interactions.",
    instruction=ORCHESTRATOR_AGENT_INSTRUCTION,
    sub_agents=[fsa_agent]
)

root_agent = orchestrator_agent