import os
from typing import Dict, Any
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
from httpx import AsyncClient

from dotenv import load_dotenv
load_dotenv(override=True)

# Configuration variables
CORPUS_NAME = f"course-selector-opt3"
RAG_CORPUS = f"projects/buoyant-purpose-475203-t9/locations/asia-southeast1/ragCorpora/7991637538768945152"


async def send_zoho_email(path_variables: Dict[str, Any], body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send email via Zoho Mail MCP server with proper enum handling.
    
    Args:
        path_variables: Object containing accountId (required)
        body: Email details with fromAddress and toAddress (required)
    """
    mcp_url = os.getenv("TESTUSER1_ZOHO_MCP", "https://course-advisor-agent-project-902810301.zohomcp.com/mcp/message?key=3f0cf7a431fdc96a5a24bb002a7d4897")
    timeout = 60
    
    try:
        # Convert scheduleType back to integer if provided as string (fix for schema issue)
        if "scheduleType" in body:
            try:
                body["scheduleType"] = int(body["scheduleType"])
            except (ValueError, TypeError):
                pass
        
        # Make HTTP request to MCP server
        async with AsyncClient(timeout=timeout) as client:
            response = await client.post(
                mcp_url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "ZohoMail_sendEmail",
                        "arguments": {
                            "path_variables": path_variables,
                            "body": body
                        }
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    return {"error": result["error"]}
                else:
                    return {"error": "Unexpected response format"}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
    except Exception as e:
        return {"error": f"Failed to call MCP server: {str(e)}"}

rag_query = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
    ),
    rag_resources=[
        rag.RagResource(
            # please fill in your own rag corpus
            # here is a sample rag corpus for testing purpose
            # e.g. projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=RAG_CORPUS,
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)