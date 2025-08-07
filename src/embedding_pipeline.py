import time
import numpy as np
from qdrant_client import QdrantClient, models
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys

# --- Gemini API Key Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    sys.exit(1)
genai.configure(api_key=GEMINI_API_KEY)

# --- Qdrant Client ---
client = QdrantClient(":memory:")

# --- Embedding Function ---
def gemini_embed(captions: list[str], task_type: str):
    result = genai.embed_content(model="models/embedding-001", content=captions, task_type=task_type)
    return result['embedding']

# --- Load Captions ---
def load_captions(filepath: str) -> list:
    """Loads captions from the specified file."""
    if not os.path.exists(filepath):
        print(f"Error: Captions file not found at {filepath}")
        return []
    
    keyframes = []
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                filename, caption = parts, parts
                keyframes.append({"id": i, "filename": filename, "caption": caption})
    return keyframes

# --- Main ---
if __name__ == "__main__":
    keyframes = load_captions("captions.txt")
    if not keyframes:
        print("Error: captions.txt not found or is empty. Please ensure the file exists and has content.")
        sys.exit(1)

    # Create a new collection with the recommended parameters
    if client.collection_exists("slam_keyframes"):
        client.delete_collection("slam_keyframes")
    client.create_collection(
        collection_name="slam_keyframes",
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        hnsw_config=models.HnswConfigDiff(m=16, ef_construct=128)
    )

    # Index the keyframes
    print(f"Indexing {len(keyframes)} keyframes...")
    captions_batch = [k["caption"] for k in keyframes]
    embeddings = gemini_embed(captions_batch, task_type="RETRIEVAL_DOCUMENT")
    client.upsert(
        collection_name="slam_keyframes",
        points=[
            models.PointStruct(id=k["id"], vector=emb, payload={"caption": k["caption"], "filename": k["filename"]})
            for k, emb in zip(keyframes, embeddings)
        ],
        wait=True,
    )
    print("Indexing complete.")

    # Sample Query
    live_caption = "a picture of an animal"
    print(f"\nQuerying with: '{live_caption}'")

    # Generate query embedding
    query_embedding = gemini_embed([live_caption], task_type="RETRIEVAL_QUERY")

    # Search the database
    search_results = client.query_points(
        collection_name="slam_keyframes",
        query=query_embedding,
        limit=5,
        search_params=models.SearchParams(hnsw_ef=256)
    ).points

    # Display Results
    print("\nTop 5 candidates:")
    for candidate in search_results:
        print(f"  - ID: {candidate.id}, Score: {candidate.score:.4f}, Caption: {candidate.payload['caption']}")