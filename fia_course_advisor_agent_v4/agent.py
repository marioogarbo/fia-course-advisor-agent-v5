from google.adk.agents import Agent
from .prompts import FIA_AGENT_INSTRUCTION
from .tools import file_search_tool, send_zoho_email

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Root agent definition
root_agent = Agent(
    name="fia_course_advisor_agent_v4",
    model="gemini-2.5-flash",
    description="An agent that advises prospective learners on suitable FIA (Fire Industry Academy) courses based on their job role, fire protection system interests, location, experience, and prior learning.",
    instruction=FIA_AGENT_INSTRUCTION,
    tools=[file_search_tool, send_zoho_email],
)