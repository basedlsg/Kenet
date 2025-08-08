import os
import time
import numpy as np
from qdrant_client import QdrantClient, models
import google.generativeai as genai
from google.cloud import aiplatform
from dotenv import load_dotenv
from tqdm import tqdm
from src.vector_db import VectorDB

# --- Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=GEMINI_API_KEY)

# --- Vector Store Configuration ---
VECTOR_STORE_TYPE = "qdrant"  # "qdrant" or "vertexai"
COLLECTION_NAME = "slam_keyframes"
CAPTIONS_FILE = "datasets/captions.txt"

# --- Google Cloud / Vertex AI Configuration (placeholders) ---
GCP_PROJECT_ID = "your-gcp-project-id"
GCP_REGION = "us-central1"
VERTEX_INDEX_ID = "your-vertex-ai-index-id"
VERTEX_INDEX_ENDPOINT_ID = "your-vertex-ai-index-endpoint-id"


def initialize_vertex_ai_client():
    """Initializes and returns the Vertex AI Index Endpoint client."""
    print("Initializing Vertex AI Vector Search client...")
    try:
        aiplatform.init(project=GCP_PROJECT_ID, location=GCP_REGION)
        index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=VERTEX_INDEX_ENDPOINT_ID
        )
        print("Vertex AI client initialized successfully.")
        return index_endpoint
    except Exception as e:
        print(f"Error initializing Vertex AI client: {e}")
        print("Please ensure you have authenticated with 'gcloud auth application-default login'")
        print("and that the specified project, region, and IDs are correct.")
        return None

# --- Initialize Clients ---
vector_store_client = None
if VECTOR_STORE_TYPE == "qdrant":
    print("Initializing in-memory Qdrant client...")
    vector_store_client = QdrantClient(":memory:")
elif VECTOR_STORE_TYPE == "vertexai":
    vector_store_client = initialize_vertex_ai_client()
else:
    raise ValueError(f"Unsupported VECTOR_STORE_TYPE: {VECTOR_STORE_TYPE}")

generation_model = genai.GenerativeModel('gemini-1.5-flash')

def get_embedding(text, task_type="RETRIEVAL_DOCUMENT"):
    """Generates an embedding for a given text."""
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type=task_type,
    )
    return result['embedding']

def populate_database():
    """
    Populates the Qdrant database with embeddings from the captions file.
    """
    db = VectorDB(collection_name=COLLECTION_NAME)
    db.create_collection()
    return db.index_captions(CAPTIONS_FILE)

def find_loop_closure_candidates(query_embedding, top_k=5, geo_filter=None):
    """Finds potential loop closure candidates from the Qdrant database."""
    db = VectorDB(collection_name=COLLECTION_NAME)
    # In a real implementation, we would need to get the 3D pose
    # and use the pruning model to predict the most promising regions.
    return db.query(query_embedding, top_k=top_k, geo_filter=geo_filter)

def verify_loop_closure(current_caption, candidate_caption):
    """Uses the Gemini model to verify if two captions describe the same location."""
    prompt = f"""
    You are a visual verification agent for a SLAM system.
    Your task is to determine if two image captions describe the same physical location,
    even if viewed from a different angle or at a different time.

    Caption A: "{current_caption}"
    Caption B: "{candidate_caption}"

    Do these two captions describe the same location?
    Answer with only "Yes" or "No".
    """
    response = generation_model.generate_content(prompt)
    return "yes" in response.text.lower()

def main_loop():
    """
    Main loop for the RAG-based SLAM process.
    """
    print("\nStarting RAG-SLAM Loop Simulation...")

    # Example: Simulate a new keyframe arriving
    new_keyframe_caption = "a desk with a computer monitor and a keyboard"
    print(f"\nNew Keyframe Caption: {new_keyframe_caption}")

    # 1. Generate embedding for the new keyframe
    start_time = time.time()
    query_embedding = get_embedding(new_keyframe_caption, task_type="RETRIEVAL_QUERY")
    print(f"Generated query embedding in {time.time() - start_time:.2f}s")

    # 2. Find potential loop closure candidates
    start_time = time.time()
    candidates = find_loop_closure_candidates(query_embedding, geo_filter="geo_1")
    print(f"Found {len(candidates)} candidates in {time.time() - start_time:.2f}s")

    if not candidates:
        print("No potential loop closures found.")
        return

    # 3. Verify candidates with the LLM
    for candidate in candidates:
        print(f"\n--- Verifying Candidate {candidate.id} (Score: {candidate.score:.4f}) ---")
        print(f"  Candidate Caption: {candidate.payload['caption']}")

        start_time = time.time()
        is_match = verify_loop_closure(new_keyframe_caption, candidate.payload['caption'])
        print(f"  Verification took {time.time() - start_time:.2f}s")

        if is_match:
            print("  ✅ VERIFIED: This is a loop closure.")
            # In a real system, you would now add a constraint to the pose graph.
            break
        else:
            print("  ❌ REJECTED: Not a loop closure.")
    else:
        print("\nNo verified loop closures found among the top candidates.")


if __name__ == "__main__":
    if populate_database():
        main_loop()