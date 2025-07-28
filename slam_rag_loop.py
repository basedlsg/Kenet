import os
import time
import numpy as np
from qdrant_client import QdrantClient, models
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm

# --- Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=GEMINI_API_KEY)

COLLECTION_NAME = "slam_keyframes"
CAPTIONS_FILE = "datasets/captions.txt"

# --- Initialize Clients ---
qdrant_client = QdrantClient(":memory:")
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
    if not os.path.exists(CAPTIONS_FILE):
        print(f"Error: Captions file not found at {CAPTIONS_FILE}")
        return False

    # --- Create Qdrant Collection ---
    if qdrant_client.collection_exists(collection_name=COLLECTION_NAME):
        qdrant_client.delete_collection(collection_name=COLLECTION_NAME)
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
    )
    print(f"Collection '{COLLECTION_NAME}' created.")

    # --- Read Captions and Generate Embeddings ---
    with open(CAPTIONS_FILE, "r") as f:
        lines = f.readlines()

    points_to_upsert = []
    for i, line in enumerate(tqdm(lines, desc="Populating Database")):
        filename, caption = line.strip().split("\t")
        embedding = get_embedding(caption)
        points_to_upsert.append(
            models.PointStruct(
                id=i,
                vector=embedding,
                payload={"filename": filename, "caption": caption}
            )
        )

    # --- Upsert Points to Qdrant ---
    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points_to_upsert,
        wait=True,
    )
    print(f"\nSuccessfully upserted {len(points_to_upsert)} points to the database.")
    return True

def find_loop_closure_candidates(query_embedding, top_k=5):
    """Finds potential loop closure candidates from the Qdrant database."""
    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
    )
    return search_result

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
    candidates_response = find_loop_closure_candidates(query_embedding)
    candidates = candidates_response.points if candidates_response else []
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