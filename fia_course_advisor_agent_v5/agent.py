from google.adk.agents import Agent
from .tools import send_zoho_email, rag_query
from .prompts import FSA_AGENT_INSTRUCTION, FSD_AGENT_INSTRUCTION, ORCHESTRATOR_AGENT_INSTRUCTION

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

fsd_agent = Agent(
    name="fire_safety_design_agent",
    model="gemini-3-pro-preview",
    description="Specialist for fire safety design and engineering courses. Provides advanced technical training recommendations for system design and senior fire protection roles.",
    instruction=FSD_AGENT_INSTRUCTION,
    tools=[rag_query, send_zoho_email],
)

fsa_agent = Agent(
    name="fire_safety_assessment_agent",
    model="gemini-3-pro-preview",
    description="Specialist for fire safety assessment, service, and maintenance training. Focuses on practical courses for equipment servicing, inspections, and compliance requirements.",
    instruction=FSA_AGENT_INSTRUCTION,
    tools=[rag_query, send_zoho_email],
)

orchestrator_agent = Agent(
    name="fia_course_advisor_orchestrator_agent",
    model="gemini-3-pro-preview",
    description="Main entry point that greets users and gathers essential information about their fire protection training needs. Routes users to appropriate specialist agents based on their role and requirements.",
    instruction=ORCHESTRATOR_AGENT_INSTRUCTION,
    sub_agents=[fsa_agent, fsd_agent]
)

root_agent = orchestrator_agent