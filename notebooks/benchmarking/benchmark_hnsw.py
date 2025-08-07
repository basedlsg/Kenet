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
        sys.exit(1)
    
    keyframes = []
    with open(filepath, "r") as f:
        for i, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) == 2:
                filename, caption = parts
                keyframes.append({"id": i, "filename": filename, "caption": caption})
    return keyframes

# --- Benchmarking Function ---
def benchmark_hnsw(keyframes: list, m: int, ef_construct: int, ef_search: int):
    """Benchmarks HNSW performance for a given set of parameters."""
    # Create a new collection with the specified parameters
    if client.collection_exists("slam_keyframes"):
        client.delete_collection("slam_keyframes")
    
    client.create_collection(
        collection_name="slam_keyframes",
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        hnsw_config=models.HnswConfigDiff(m=m, ef_construct=ef_construct)
    )

    # Index the keyframes
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

    # Run a series of queries and measure performance
    query_latencies = []
    recalls = []
    for i in range(100):
        # Select a random keyframe as the query
        query_keyframe = np.random.choice(keyframes)
        query_caption = query_keyframe["caption"]
        query_embedding = gemini_embed([query_caption], task_type="RETRIEVAL_QUERY")[0]

        # Measure query latency
        start_time = time.perf_counter()
        search_results = client.query_points(
            collection_name="slam_keyframes",
            query=query_embedding,
            limit=10,
            search_params=models.SearchParams(hnsw_ef=ef_search)
        )
        end_time = time.perf_counter()
        query_latencies.append((end_time - start_time) * 1000)

        # Measure recall
        retrieved_ids = {result.id for result in search_results.points}
        ground_truth_ids = {query_keyframe["id"]}
        recall = len(retrieved_ids.intersection(ground_truth_ids)) / len(ground_truth_ids)
        recalls.append(recall)

    return np.mean(query_latencies), np.mean(recalls)

# --- Main ---
if __name__ == "__main__":
    keyframes = load_captions("captions.txt")
    if not keyframes:
        print("Error: No keyframes were loaded. Exiting.")
        sys.exit(1)

    # Define the parameter grid to search
    m_values = [8, 16, 32, 64]
    ef_construct_values = [64, 128, 256, 512]
    ef_search_values = [32, 64, 128, 256]

    # Run the benchmark
    results = []
    for m in m_values:
        for ef_construct in ef_construct_values:
            for ef_search in ef_search_values:
                print(f"Testing m={m}, ef_construct={ef_construct}, ef_search={ef_search}...")
                latency, recall = benchmark_hnsw(keyframes, m, ef_construct, ef_search)
                results.append({
                    "m": m,
                    "ef_construct": ef_construct,
                    "ef_search": ef_search,
                    "latency_ms": latency,
                    "recall": recall
                })
                print(f"  Result: latency={latency:.2f}ms, recall={recall:.2f}")

    # Print the best results
    best_latency = min(results, key=lambda x: x["latency_ms"])
    best_recall = max(results, key=lambda x: x["recall"])
    print(f"\nBest latency: {best_latency['latency_ms']:.2f}ms (recall={best_latency['recall']:.2f}) with m={best_latency['m']}, ef_construct={best_latency['ef_construct']}, ef_search={best_latency['ef_search']}")
    print(f"Best recall: {best_recall['recall']:.2f} (latency={best_recall['latency_ms']:.2f}ms) with m={best_recall['m']}, ef_construct={best_recall['ef_construct']}, ef_search={best_recall['ef_search']}")