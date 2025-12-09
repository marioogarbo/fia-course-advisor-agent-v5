from google.adk.agents.llm_agent import Agent
from .prompts import REDMEN_SYSTEM_INSTRUCTION
from .tools import Simpro

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Initialize the Simpro client
simpro_client = Simpro()

root_agent = Agent(
    name='redmen_simpro_agent',
    model='gemini-2.5-flash',
    description='An AI assisstant that helps users access information about Redmen\'s employees and customers from the Simpro system.',
    instruction=REDMEN_SYSTEM_INSTRUCTION,
    tools=[
        simpro_client.get_companies,
        simpro_client.get_employees,
        simpro_client.get_employee,
        simpro_client.get_customers,
        simpro_client.get_customer,
        simpro_client.get_jobs,
        simpro_client.get_job,
        simpro_client.get_job_attachments,
        simpro_client.get_jobs_reports_ops,
        simpro_client.get_jobs_reports_financials,
        simpro_client.get_customers_of_company,
        simpro_client.get_leads,
        simpro_client.get_lead,
        simpro_client.get_quotes,
        simpro_client.get_quote
    ],
)