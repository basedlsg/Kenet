import time
import numpy as np
from qdrant_client import QdrantClient, models
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys
from tqdm import tqdm

# --- Gemini API Key Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    sys.exit(1)
genai.configure(api_key=GEMINI_API_KEY)

class VectorDB:
    def __init__(self, collection_name="slam_keyframes"):
        self.client = QdrantClient(":memory:")
        self.collection_name = collection_name

    def get_embedding(self, text, task_type="RETRIEVAL_DOCUMENT"):
        """Generates an embedding for a given text."""
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type=task_type,
        )
        return result['embedding']

    def create_collection(self, vector_size=768, distance=models.Distance.COSINE):
        if self.client.collection_exists(collection_name=self.collection_name):
            self.client.delete_collection(collection_name=self.collection_name)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(size=vector_size, distance=distance),
        )

    def index_captions(self, captions_file: str, batch_size: int = 32):
        """Indexes captions from a file in batches."""
        if not os.path.exists(captions_file):
            print(f"Error: Captions file not found at {captions_file}")
            return False

        with open(captions_file, "r") as f:
            lines = f.readlines()

        points_to_upsert = []
        for i in range(0, len(lines), batch_size):
            batch_lines = lines[i:i+batch_size]
            captions_data = [line.strip().split("\t") for line in batch_lines if "\t" in line]
            
            text_captions = [data for data in captions_data]
            
            if not text_captions:
                continue

            embeddings = self.get_embedding(text_captions, task_type="RETRIEVAL_DOCUMENT")
            
            points_to_upsert.extend([
                models.PointStruct(
                    id=i + j,
                    vector=embedding,
                    payload={"filename": captions_data[j], "caption": captions_data[j]}
                )
                for j, embedding in enumerate(embeddings)
            ])

        if points_to_upsert:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points_to_upsert,
                wait=True,
            )
        return True

    def query(self, query_embedding, top_k=5, geo_filter=None):
        """Queries the vector database with an optional geometric filter."""
        query_filter = None
        if geo_filter:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="geometric_descriptor",
                        match=models.MatchValue(value=geo_filter),
                    )
                ]
            )
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            search_params=models.SearchParams(hnsw_ef=128),
        )
        if search_result and search_result.points:
            return search_result.points
        return None