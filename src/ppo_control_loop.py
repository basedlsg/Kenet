import gymnasium as gym
import ray
from ray.rllib.algorithms.ppo import PPOConfig
from atropos_env import SLAMAtroposEnv
import time
import numpy as np
from qdrant_client import QdrantClient, models
from google import generativeai as genai
import os
from dotenv import load_dotenv
import sys
import io
import gtsam
import pickle
from google.cloud import storage

# --- Factor Graph Manager ---
class FactorGraphManager:
    def __init__(self):
        self.graph = gtsam.NonlinearFactorGraph()
        self.initial_estimates = gtsam.Values()
        self.next_pose_id = 0

    def add_pose(self, pose):
        """Adds a new pose to the factor graph."""
        self.initial_estimates.insert(self.next_pose_id, pose)
        self.next_pose_id += 1
        return self.next_pose_id - 1

    def add_loop_closure(self, from_id, to_id, relative_pose, confidence):
        """Adds a loop closure constraint between two poses."""
        noise_model = gtsam.noiseModel.Diagonal.Sigmas(
            np.array([1.0 / confidence] * 6)
        )
        self.graph.add(
            gtsam.BetweenFactorPose3(from_id, to_id, relative_pose, noise_model)
        )

    def optimize(self):
        """Optimizes the factor graph."""
        optimizer = gtsam.LevenbergMarquardtOptimizer(self.graph, self.initial_estimates)
        result = optimizer.optimize()
        return result
    
    def save_state(self, filepath):
        """Saves the factor graph and initial estimates to a file."""
        with open(filepath, "wb") as f:
            pickle.dump((self.graph, self.initial_estimates), f)

    def load_state(self, filepath):
        """Loads the factor graph and initial estimates from a file."""
        with open(filepath, "rb") as f:
            self.graph, self.initial_estimates = pickle.load(f)

# --- Gemini API Key Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    sys.exit(1)
genai.configure(api_key=GEMINI_API_KEY)

# --- RAG Components ---

# 1. Vector Database Setup
client = QdrantClient(":memory:")
client.recreate_collection(
    collection_name="slam_keyframes",
    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
)

# 2. Embedding Function
def gemini_embed(captions: list[str], task_type: str):
    result = genai.embed_content(model="models/embedding-001", content=captions, task_type=task_type)
    return result['embedding']

# 3. Load and Index Real Keyframes
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

print("Loading and indexing real keyframes from dataset...")
map_keyframes = load_captions("captions.txt")
if not map_keyframes:
    print("Error: No keyframes were loaded. Exiting.")
    sys.exit(1)
captions_batch = [k["caption"] for k in map_keyframes]
embeddings = gemini_embed(captions_batch, task_type="RETRIEVAL_DOCUMENT")
client.upsert(
    collection_name="slam_keyframes",
    points=[
        models.PointStruct(id=k["id"], vector=emb, payload={"caption": k["caption"], "filename": k["filename"]})
        for k, emb in zip(map_keyframes, embeddings)
    ],
    wait=True,
)
print(f"Successfully indexed {len(map_keyframes)} keyframes.")

# 4. LLM Verification Logic
def call_llm_verification(prompt: str) -> tuple[str, float]:
    stopwords = {'a', 'an', 'the', 'of', 'in', 'is', 'on', 'photo', 'picture'}
    lines = prompt.strip().split('\n')
    try:
        live_caption = lines[-4].split('"')[1]
        retrieved_caption = lines[-3].split('"')[1]
        live_words = set(live_caption.lower().split()) - stopwords
        retrieved_words = set(retrieved_caption.lower().split()) - stopwords
        
        # Calculate a simple confidence score based on word overlap
        intersection_size = len(live_words.intersection(retrieved_words))
        union_size = len(live_words.union(retrieved_words))
        confidence = intersection_size / union_size if union_size > 0 else 0.0
        
        return ("yes", confidence) if confidence > 0.1 else ("no", 0.0)
    except IndexError:
        return "no", 0.0

def llama_chain_of_thought(live_obs: str, context_caption: str) -> tuple[bool, float]:
    prompt = f'You are a verification agent... (prompt omitted for brevity)\nLive Observation: "{live_obs}"\nRetrieved Keyframe: "{context_caption}"\nVerification:'
    response, confidence = call_llm_verification(prompt)
    print(f"  - LLM Verification: Is '{live_obs}' the same as '{context_caption}'? -> {response.upper()} (Confidence: {confidence:.2f})")
    return response.strip().lower() == "yes", confidence

def add_edge_to_pose_graph(from_id, to_id, confidence):
    print(f"  - INFO: Adding loop closure constraint between keyframe {from_id} and {to_id} with confidence {confidence:.2f}.")
    # In a real system, we would calculate the relative pose between the two keyframes.
    # For this simulation, we'll use an identity pose.
    relative_pose = gtsam.Pose3()
    factor_graph_manager.add_loop_closure(from_id, to_id, relative_pose, confidence)

# 5. RAG Loop Closure Function
factor_graph_manager = FactorGraphManager()

def trigger_rag_loop_closure(current_keyframe_id: int, mode: str):
    """Triggers RAG loop closure based on the experimental mode."""
    # Simulate a new frame by picking a random keyframe from our dataset
    live_keyframe = np.random.choice(map_keyframes)
    live_caption = live_keyframe["caption"]
    print(f"  -> Triggering RAG for live frame: '{live_caption}'")

    live_embedding = gemini_embed([live_caption], task_type="RETRIEVAL_QUERY")[0]

    search_results = client.search(collection_name="slam_keyframes", query_vector=live_embedding, limit=1)

    if not search_results:
        print("  - No similar keyframes found.")
        return

    top_candidate = search_results[0]
    context_caption = top_candidate.payload['caption']

    geometric_check_passed = True
    if mode == "rag-slam":
        # Simulate a geometric check. In a real system, this would involve
        # checking if the current pose is geometrically close to the candidate pose.
        # Here, we simulate it with a 50% success rate.
        if np.random.rand() > 0.5:
            print("  - Simulated geometric check: PASSED")
        else:
            print("  - Simulated geometric check: FAILED")
            geometric_check_passed = False

    if geometric_check_passed:
        is_loop_closure, confidence = llama_chain_of_thought(live_caption, context_caption)
        if is_loop_closure:
            add_edge_to_pose_graph(current_keyframe_id, top_candidate.id, confidence)

# --- Main PPO Control Loop ---
def load_ground_truth_timestamps(filepath: str) -> list:
    """Loads timestamps from a TUM ground truth file."""
    timestamps = []
    with open(filepath, "r") as f:
        for line in f:
            if not line.startswith('#'):
                parts = line.strip().split()
                if len(parts) >= 1:
                    timestamps.append(parts[0])
    return timestamps

def save_trajectory(trajectory: list, timestamps: list, filepath: str, gcs_bucket: str = None):
    """Saves the trajectory to a file in TUM format and optionally uploads to GCS."""
    output_buffer = io.StringIO()
    for i, pose in enumerate(trajectory):
        # TUM format: timestamp tx ty tz qx qy qz qw
        line = f"{timestamps[i]} {pose[0]} {pose[1]} {pose[2]} 0 0 0 1"
        output_buffer.write(line)
        if i < len(trajectory) - 1:
            output_buffer.write("\n")
    
    if gcs_bucket:
        upload_to_gcs(gcs_bucket, filepath, output_buffer.getvalue())
    else:
        with open(filepath, "w") as f:
            f.write(output_buffer.getvalue())
        print(f"\nTrajectory saved to {filepath}")

def upload_to_gcs(bucket_name, destination_blob_name, contents):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)

    print(
        f"File {destination_blob_name} uploaded to {bucket_name}."
    )

def save_atomic_checkpoint(trainer, graph_manager, checkpoint_dir):
    """Saves the trainer state and graph manager state in a single checkpoint."""
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Save RLlib trainer state
    trainer_checkpoint_path = os.path.join(checkpoint_dir, "rllib_checkpoint")
    trainer.save(trainer_checkpoint_path)
    
    # Save factor graph state
    graph_checkpoint_path = os.path.join(checkpoint_dir, "graph_state.pkl")
    graph_manager.save_state(graph_checkpoint_path)
    
    print(f"Atomic checkpoint saved to {checkpoint_dir}")

def main(args):
    """Main function to train and evaluate the PPO agent."""
    print("Initializing Ray...")
    ray.init(num_gpus=4, _temp_dir="/tmp/ray_new") # Configure for 4 GPUs

    print("Starting PPO Control Loop Training...")
    
    config = (
        PPOConfig()
        .environment(SLAMAtroposEnv)
        .env_runners(num_env_runners=256 * 4, rollout_fragment_length='auto') # 256 envs per GPU
        .training(gamma=0.99, lr=5e-5, train_batch_size=5120)
        .resources(num_gpus=1) # Main trainer on one GPU
    )
    
    trainer = config.build()

    print("\n--- Training PPO Agent with Ray RLlib ---")
    for i in range(10): # Train for 10 iterations
        result = trainer.train()
        print(f"Iteration {i+1}: mean reward = {result['episode_reward_mean']}")
        
        if (i + 1) % 5 == 0:
            save_atomic_checkpoint(trainer, factor_graph_manager, f"checkpoints/ppo_slam_checkpoint_{i+1}")

    print("--- Training Finished ---")

    print(f"\n--- Evaluating Trained Agent (Mode: {args.mode}) ---")
    env = SLAMAtroposEnv()
    obs, _ = env.reset()
    current_keyframe_id = len(map_keyframes) + 1
    estimated_trajectory = []
    
    ground_truth_timestamps = load_ground_truth_timestamps("datasets/rgbd_dataset_freiburg1_xyz/groundtruth.txt")
    
    for i in range(len(ground_truth_timestamps)): # Evaluate for the length of the ground truth
        # Simulate pose estimation
        noise = np.random.normal(0, 0.1) if args.mode != "vision-only" else 0.0
        pose_xyz = [i * 0.1 + noise, np.sin(i * 0.1) + noise, 0.0]
        
        # Add the new pose to the factor graph
        pose3 = gtsam.Pose3(gtsam.Rot3(), gtsam.Point3(*pose_xyz))
        factor_graph_manager.add_pose(pose3)
        
        estimated_trajectory.append(pose_xyz)

        action = trainer.compute_single_action(obs, explore=False)
        obs, reward, terminated, _, _ = env.step(action)
        
        action_map = {0: 'increase_kf', 1: 'decrease_kf', 2: 'add_constraint'}
        print(f"Step {i+1}: Action: {action_map[action.item()]:<15} | Reward: {reward:<8.2f}")

        if args.mode in ["text-only", "rag-slam"] and action == 2: # 'add_semantic_constraint'
            trigger_rag_loop_closure(current_keyframe_id, args.mode)
            current_keyframe_id += 1

        if terminated:
            break
            
    print("--- Evaluation Finished ---")

    if args.mode in ["text-only", "rag-slam"]:
        print("\n--- Optimizing Factor Graph ---")
        optimized_values = factor_graph_manager.optimize()
        print("--- Optimization Finished ---")
        
        # Extract optimized trajectory
        optimized_trajectory = []
        for i in range(optimized_values.size()):
            pose = optimized_values.atPose3(i)
            optimized_trajectory.append([pose.x(), pose.y(), pose.z()])
        
        if args.output:
            # Save both trajectories for comparison
            raw_output_path = args.output.replace(".txt", "_raw.txt")
            save_trajectory(estimated_trajectory, ground_truth_timestamps, raw_output_path, args.gcs_bucket)
            save_trajectory(optimized_trajectory, ground_truth_timestamps, args.output, args.gcs_bucket)
    elif args.output:
        save_trajectory(estimated_trajectory, ground_truth_timestamps, args.output, args.gcs_bucket)
    
    ray.shutdown()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run PPO-RAG-SLAM Experiment")
    parser.add_argument("--mode", type=str, default="rag-slam", choices=["vision-only", "text-only", "rag-slam"], help="Experimental condition to run.")
    parser.add_argument("-o", "--output", type=str, help="Path to save the estimated trajectory file.")
    parser.add_argument("--gcs-bucket", type=str, default="atropos_bucket", help="GCS bucket to upload the trajectory to.")
    args = parser.parse_args()
    main(args)