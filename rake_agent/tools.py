from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Configuration variables
CORPUS_NAME = f"redadair-rake-documents"
RAG_CORPUS = f"projects/buoyant-purpose-475203-t9/locations/asia-southeast1/ragCorpora/2305843009213693952"

rag_query = VertexAiRagRetrieval(
    name='retrieve_rag_documentation',
    description=(
        'Use this tool to retrieve documentation and reference materials for the question from the RAG corpus,'
    ),
    rag_resources=[
        rag.RagResource(
            # please fill in syour own rag corpus
            # here is a sample rag corpus for testing purpose
            # e.g. projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=RAG_CORPUS,
        )
    ],
    similarity_top_k=10,
    vector_distance_threshold=0.6,
)