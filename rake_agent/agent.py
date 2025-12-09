from google.adk.agents.llm_agent import Agent
from .tools import rag_query
from .prompts import RAKE_AGENT_INSTRUCTION

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

root_agent = Agent(
    name='rake_agent',
    model='gemini-2.5-flash',
    description='A RAG-based knowledge assistant that provides information exclusively from the documentation corpus.',
    instruction=RAKE_AGENT_INSTRUCTION,
    tools=[rag_query],
)