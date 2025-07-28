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
    print("Please set the GEMINI_API_KEY environment variable in your .env file.")
    sys.exit(1)
genai.configure(api_key=GEMINI_API_KEY)
# --- End of Gemini API Key Configuration ---

# 1. Vector Database Setup
# Use a local, in-memory QDrant instance for this example
client = QdrantClient(":memory:")

# Create a collection for our vectors
if client.collection_exists(collection_name="slam_keyframes"):
    client.delete_collection(collection_name="slam_keyframes")

client.create_collection(
    collection_name="slam_keyframes",
    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
)

# 2. Embedding Generation Function (Real Implementation)
def gemini_embed(captions: list[str], task_type: str):
    """
    Generates embeddings for a batch of captions using the Gemini API.
    """
    # For embeddings, you can use the 'embedding-001' model
    result = genai.embed_content(
        model="models/embedding-001",
        content=captions,
        task_type=task_type,
    )
    return result['embedding']

# 3. Indexing Sample Keyframes
map_keyframes = [
    {"id": 1, "caption": "a photo of a cat"},
    {"id": 2, "caption": "a photo of a dog"},
    {"id": 3, "caption": "a photo of a bird"},
    {"id": 4, "caption": "a photo of a house"},
    {"id": 5, "caption": "a photo of a car"},
]

print("Indexing keyframes...")
# Create a batch of captions
captions_batch = [k["caption"] for k in map_keyframes]

# Get embeddings for the whole batch
embeddings = gemini_embed(captions_batch, task_type="RETRIEVAL_DOCUMENT")

# Upsert points in a batch
client.upsert(
    collection_name="slam_keyframes",
    points=[
        models.PointStruct(id=keyframe["id"], vector=embedding, payload={"caption": keyframe["caption"]})
        for keyframe, embedding in zip(map_keyframes, embeddings)
    ],
    wait=True,
)
print("Indexing complete.")

# 4. Sample Query and Performance Measurement
live_caption = "a picture of an animal"
print(f"\nQuerying with: '{live_caption}'")

start_time = time.perf_counter()

# Generate query embedding
z_live = gemini_embed([live_caption], task_type="RETRIEVAL_QUERY")[0]

# Search the database
candidates = client.search(
    collection_name="slam_keyframes",
    query_vector=z_live,
    limit=5,
)

end_time = time.perf_counter()

print(f"Query completed in {(end_time - start_time) * 1000:.2f}ms")

# 5. Display Results
print("\nTop 5 candidates:")
for candidate in candidates:
    print(f"  - ID: {candidate.id}, Score: {candidate.score:.4f}, Caption: {candidate.payload['caption']}")
