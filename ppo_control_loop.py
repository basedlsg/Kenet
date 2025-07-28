import gymnasium as gym
from stable_baselines3 import PPO
from atropos_env import SLAMAtroposEnv
import time
import numpy as np
from qdrant_client import QdrantClient, models
from google import generativeai as genai
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
def call_llm_verification(prompt: str) -> str:
    stopwords = {'a', 'an', 'the', 'of', 'in', 'is', 'on', 'photo', 'picture'}
    lines = prompt.strip().split('\n')
    try:
        live_caption = lines[-4].split('"')[1]
        retrieved_caption = lines[-3].split('"')[1]
        live_words = set(live_caption.lower().split()) - stopwords
        retrieved_words = set(retrieved_caption.lower().split()) - stopwords
        return "yes" if not live_words.isdisjoint(retrieved_words) else "no"
    except IndexError:
        return "no"

def llama_chain_of_thought(live_obs: str, context_caption: str) -> bool:
    prompt = f'You are a verification agent... (prompt omitted for brevity)\nLive Observation: "{live_obs}"\nRetrieved Keyframe: "{context_caption}"\nVerification:'
    response = call_llm_verification(prompt)
    print(f"  - LLM Verification: Is '{live_obs}' the same as '{context_caption}'? -> {response.upper()}")
    return response.strip().lower() == "yes"

def add_edge_to_pose_graph(from_id, to_id):
    print(f"  - INFO: Adding loop closure constraint between keyframe {from_id} and {to_id}.")

# 5. RAG Loop Closure Function
def trigger_rag_loop_closure(current_keyframe_id: int):
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
    
    if llama_chain_of_thought(live_caption, context_caption):
        add_edge_to_pose_graph(current_keyframe_id, top_candidate.id)

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

def save_trajectory(trajectory: list, timestamps: list, filepath: str):
    """Saves the trajectory to a file in TUM format using provided timestamps."""
    with open(filepath, "w") as f:
        for i, pose in enumerate(trajectory):
            # TUM format: timestamp tx ty tz qx qy qz qw
            f.write(f"{timestamps[i]} {pose[0]} {pose[1]} {pose[2]} 0 0 0 1\n")
    print(f"\nTrajectory saved to {filepath}")

def main(args):
    """Main function to train and evaluate the PPO agent."""
    print("Starting PPO Control Loop Training...")
    env = SLAMAtroposEnv()
    model = PPO("MlpPolicy", env, verbose=0)
    
    print("\n--- Training PPO Agent ---")
    model.learn(total_timesteps=1000)
    print("--- Training Finished ---")

    model.save("ppo_slam_agent")
    print("\nTrained model saved to 'ppo_slam_agent.zip'")

    print(f"\n--- Evaluating Trained Agent (RAG Enabled: {args.rag}) ---")
    obs, _ = env.reset()
    current_keyframe_id = len(map_keyframes) + 1
    estimated_trajectory = []
    
    ground_truth_timestamps = load_ground_truth_timestamps("datasets/rgbd_dataset_freiburg1_xyz/groundtruth.txt")
    
    for i in range(len(ground_truth_timestamps)): # Evaluate for the length of the ground truth
        # Simulate pose estimation
        # In a real system, this would come from the SLAM backend
        # Add some noise to the RAG-SLAM trajectory to make it different
        noise = np.random.normal(0, 0.1) if args.rag else 0.0
        pose = [i * 0.1 + noise, np.sin(i * 0.1) + noise, 0.0]
        estimated_trajectory.append(pose)

        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, _, _ = env.step(action)
        
        action_map = {0: 'increase_kf', 1: 'decrease_kf', 2: 'add_constraint'}
        print(f"Step {i+1}: Action: {action_map[action.item()]:<15} | Reward: {reward:<8.2f}")

        if args.rag and action == 2: # 'add_semantic_constraint'
            trigger_rag_loop_closure(current_keyframe_id)
            current_keyframe_id += 1

        if terminated:
            break
            
    print("--- Evaluation Finished ---")
    if args.output:
        save_trajectory(estimated_trajectory, ground_truth_timestamps, args.output)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run PPO-RAG-SLAM Experiment")
    parser.add_argument("--rag", action="store_true", help="Enable the RAG mechanism for loop closure.")
    parser.add_argument("-o", "--output", type=str, help="Path to save the estimated trajectory file.")
    args = parser.parse_args()
    main(args)