from google.adk.agents import Agent
from .tools import file_search_tool

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Root agent definition
root_agent = Agent(
    name="file_search_agent",
    model="gemini-2.5-flash",
    description="An agent that answers questions using indexed documents.",
    instruction="""
    You are a helpful assistant that answers questions using indexed documents.
    
    When the user asks a question:
    1. Use the 'file_search_tool' tool to retrieve relevant information from the documents.
    2. If the tool returns citations, include them in your response.
    3. If the tool returns an error, inform the user politely.
    """,
    tools=[file_search_tool],
)