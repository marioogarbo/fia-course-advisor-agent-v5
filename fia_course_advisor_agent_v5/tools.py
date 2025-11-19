import os
import json
import re
from typing import Dict, Any, List
from vertexai.preview import rag
from httpx import AsyncClient

# Configuration variables
CORPUS_NAME = f"course-selector-opt1"
RAG_CORPUS = f"projects/buoyant-purpose-475203-t9/locations/asia-southeast1/ragCorpora/5685794529555251200"
DEFAULT_TOP_K = 10
DEFAULT_VECTOR_DISTANCE_THRESHOLD = 0.6


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


def _parse_course_from_text(text: str) -> Dict[str, Any]:
    """
    Parse course information from RAG text response.
    Extracts course code, title, delivery mode, duration, prerequisites, state, cost, etc.
    
    Args:
        text (str): Raw text from RAG corpus
    
    Returns:
        dict: Structured course information
    """
    course = {
        "raw_text": text[:500],  # Store truncated raw text for reference
        "code": "",
        "title": "",
        "delivery_mode": "To be confirmed",
        "duration": "To be confirmed",
        "prerequisites": [],
        "state": "NSW",  # Default
        "cost": "To be confirmed",
        "rpl_eligible": False,
    }
    
    # Extract course code (e.g., FSD101, FSA202, CHCDF, etc.)
    code_match = re.search(r'\b([A-Z]{2,4}\d{2,4})\b', text)
    if code_match:
        course["code"] = code_match.group(1)
    
    # Extract state abbreviations (NSW, VIC, QLD, WA, SA, TAS, ACT, NT)
    state_match = re.search(r'\b(NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\b', text)
    if state_match:
        course["state"] = state_match.group(1)
    
    # Extract delivery mode
    text_lower = text.lower()
    if any(term in text_lower for term in ["face-to-face", "in-person", "classroom", "on-site"]):
        course["delivery_mode"] = "Face-to-face"
    elif "online" in text_lower or "virtual" in text_lower:
        course["delivery_mode"] = "Online"
    elif "blended" in text_lower or "hybrid" in text_lower:
        course["delivery_mode"] = "Blended"
    elif "online and" in text_lower or "face-to-face and" in text_lower:
        course["delivery_mode"] = "Blended"
    
    # Extract duration (e.g., "12 weeks", "3 months", "40 hours")
    duration_match = re.search(r'(\d+\.?\d*)\s*(weeks?|months?|days?|hours?|years?)', text_lower)
    if duration_match:
        num = duration_match.group(1)
        unit = duration_match.group(2)
        course["duration"] = f"{num} {unit.capitalize()}"
    
    # Extract cost (e.g., $5000, $2,500.00)
    cost_match = re.search(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', text)
    if cost_match:
        course["cost"] = cost_match.group(0)
    
    # Check for RPL eligibility
    if any(term in text_lower for term in ["rpl", "recognition of prior learning", "credit transfer", "credit toward"]):
        course["rpl_eligible"] = True
    
    # Try to extract title - look for course name patterns
    lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 10]
    
    # Prefer lines that look like course titles (contain "course", "diploma", "certificate", etc.)
    title_keywords = ["course", "diploma", "certificate", "qualification", "training", "program"]
    for line in lines[:5]:  # Check first few lines
        if any(keyword in line.lower() for keyword in title_keywords):
            course["title"] = line
            break
    
    # If no title found with keywords, use first substantial line
    if not course["title"] and lines:
        first_line = lines[0]
        # Avoid using lines that are just metadata
        if not any(x in first_line.lower() for x in ["code:", "duration:", "cost:", "state:"]):
            course["title"] = first_line
    
    # Extract prerequisites if present
    prereq_patterns = [
        r'(?:prerequisite|requirement|require)[s]?:?\s*(.+?)(?:\n|$)',
        r'(?:entry requirement)[s]?:?\s*(.+?)(?:\n|$)',
        r'(?:eligibility)[:\s]+(.+?)(?:\n|$)',
    ]
    
    for pattern in prereq_patterns:
        prereq_section = re.search(pattern, text, re.IGNORECASE)
        if prereq_section:
            prereq_text = prereq_section.group(1)
            # Split by comma, "and", or semicolon
            prereqs = re.split(r',\s*|\s+and\s+|;\s*', prereq_text)
            course["prerequisites"] = [p.strip() for p in prereqs if p.strip() and len(p.strip()) > 3]
            break
    
    # Clean up title - remove extra whitespace
    if course["title"]:
        course["title"] = " ".join(course["title"].split())
    
    return course


def rag_query(query: str) -> Dict[str, Any]:
    """
    Query a Vertex AI RAG corpus with a user question and return structured course information.
    Parses raw results into organized course objects with specific fields.

    Args:
        query (str): The text query to search for in the corpus

    Returns:
        dict: Structured course results with status, message, and parsed courses array
    """
    try:
        # Perform the query
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=RAG_CORPUS
                )
            ],
            text=query,
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=DEFAULT_TOP_K,
                filter=rag.Filter(vector_distance_threshold=DEFAULT_VECTOR_DISTANCE_THRESHOLD),
            ),
        )

        # Process the response into structured course format
        courses = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                raw_text = ctx_group.text if hasattr(ctx_group, "text") else ""
                score = ctx_group.score if hasattr(ctx_group, "score") else 0.0
                
                # Parse course information from raw text
                course_data = _parse_course_from_text(raw_text)
                course_data["relevance_score"] = float(score)
                
                courses.append(course_data)

        # If we didn't find any results
        if not courses:
            return {
                "status": "warning",
                "message": f"No courses found for query: '{query}'. Please try a different search or contact our admin team.",
                "query": query,
                "corpus_name": CORPUS_NAME,
                "courses": [],
                "count": 0,
            }

        return {
            "status": "success",
            "message": f"Found {len(courses)} course(s) matching your criteria",
            "query": query,
            "corpus_name": CORPUS_NAME,
            "courses": courses,
            "count": len(courses),
        }

    except Exception as e:
        error_msg = f"Error querying courses: {str(e)}"
        return {
            "status": "error",
            "message": error_msg,
            "query": query,
            "corpus_name": CORPUS_NAME,
            "courses": [],
            "count": 0,
        }