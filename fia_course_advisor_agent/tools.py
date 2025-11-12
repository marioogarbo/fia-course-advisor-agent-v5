import os
import time
from google import genai
from google.genai import types

# ─────────────────────────────────────────────────────────────────────────────
# 1. Setup: Create your File Search Store (same as before)
# ─────────────────────────────────────────────────────────────────────────────

client = genai.Client()

# Create the File Search store with an optional display name
file_search_store = client.file_search_stores.create(config={'display_name': 'my-rag-store'})
store_name = f"{file_search_store.name}"
print("Created store:", store_name)

# Upload and index your file
# Use absolute path to avoid path resolution issues
local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "course-selector-opt2.xlsx"))
operation = client.file_search_stores.upload_to_file_search_store(
    file=local_path,
    file_search_store_name=store_name,
    config={'display_name': os.path.basename(local_path)}
)

# Poll until indexing completes
while not operation.done:
    time.sleep(2)
    operation = client.operations.get(operation)

print("Upload+index complete.")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Wrap File Search as a Custom ADK Tool
# ─────────────────────────────────────────────────────────────────────────────

def file_search_tool(query: str, metadata_filter: str = "") -> dict:
    """
    Searches the indexed documents in the File Search store and returns a grounded answer.
    
    Args:
        query: The user's question to answer from the documents.
        metadata_filter: Optional AIP-160 filter (e.g., 'doc_type="manual"').
    
    Returns:
        dict: Contains 'status', 'answer', and 'citations' keys.
    """
    try:
        # Build the FileSearch tool config
        file_search_config = types.FileSearch(file_search_store_names=[store_name])

        if metadata_filter:
            file_search_config.metadata_filter = metadata_filter
        
        # Call Gemini with File Search tool
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(file_search=file_search_config)]
            )
        )
        
        answer = response.text
        
        # Extract citations from grounding metadata
        citations = []
        if response.candidates:
            gm = response.candidates[0].grounding_metadata
            if gm and gm.grounding_chunks:
                for chunk in gm.grounding_chunks:
                    if chunk.web:
                        citations.append({
                            'title': chunk.web.title or 'Document',
                            'uri': chunk.web.uri
                        })
        
        return {
            "status": "success",
            "answer": answer,
            "citations": citations
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }