from google.adk.agents import Agent
from .tools import send_zoho_email, rag_query
from .prompts import FIA_AGENT_INSTRUCTION

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Main FIA Course Advisor Agent
root_agent = Agent(
    name="fia_course_advisor_agent_v2",
    model="gemini-2.5-flash",
    description="An agent that advises prospective learners on suitable FIA (Fire Industry Academy) courses based on their job role, fire protection system interests, location, experience, and prior learning.",
    instruction=FIA_AGENT_INSTRUCTION,
    tools=[rag_query, send_zoho_email],
)