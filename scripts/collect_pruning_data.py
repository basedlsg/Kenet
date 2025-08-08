import json
import numpy as np
from src.atropos_env import SLAMAtroposEnv
from src.vector_db import VectorDB

def collect_data(num_steps: int, output_file: str):
    """Collects training data for the geometric pruning model."""
    env = SLAMAtroposEnv()
    db = VectorDB()
    db.create_collection()
    db.index_captions("datasets/captions.txt")

    with open(output_file, "w") as f:
        for _ in range(num_steps):
            obs, _ = env.reset()
            query_embedding = db.get_embedding(obs, task_type="RETRIEVAL_QUERY")
            # In a real implementation, we would need to get the 3D pose
            # and the positive and negative candidate IDs.
            query_3d_pose = [0.0, 0.0, 0.0]
            positive_candidate_ids = []
            negative_candidate_ids = []
            data = {
                "query_embedding": query_embedding.tolist(),
                "query_3d_pose": query_3d_pose,
                "positive_candidate_ids": positive_candidate_ids,
                "negative_candidate_ids": negative_candidate_ids,
            }
            f.write(json.dumps(data) + "\n")

if __name__ == "__main__":
    collect_data(100, "pruning_data.jsonl")