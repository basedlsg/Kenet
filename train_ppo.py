# train_ppo.py
# This script trains a PPO agent on the SLAMAtroposEnv.
# Dependencies: stable-baselines3, gymnasium, torch

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

from atropos_env import SLAMAtroposEnv

# --- 1. Instantiate the Environment ---
print("Initializing environment...")
env = SLAMAtroposEnv()

# It's good practice to check the environment to ensure it's compatible with stable-baselines3
try:
    check_env(env)
    print("Environment check passed!")
except Exception as e:
    print(f"Environment check failed: {e}")
    exit()

# --- 2. Create the PPO Agent ---
# We use the "MlpPolicy" because our observation space is a flat vector.
# The agent will learn a policy to map observations to actions.
print("Creating PPO agent...")
model = PPO(
    "MlpPolicy", 
    env, 
    verbose=1,
    tensorboard_log="./ppo_slam_tensorboard/"
)

# --- 3. Train the Agent ---
# The learn() method starts the training process.
# We'll train for 50,000 steps as a demonstration.
TRAINING_STEPS = 50_000
print(f"Starting training for {TRAINING_STEPS} timesteps...")
model.learn(total_timesteps=TRAINING_STEPS)
print("Training complete.")

# --- 4. Save the Trained Model ---
MODEL_PATH = "ppo_slam_agent.zip"
print(f"Saving trained model to {MODEL_PATH}...")
model.save(MODEL_PATH)
print("Model saved.")

# --- 5. Demonstrate Loading and Using the Model ---
print("\n--- Demonstrating loaded model ---")
# Load the trained agent
loaded_model = PPO.load(MODEL_PATH)

# Get a sample observation from the environment
obs, _ = env.reset()
print(f"Sample observation: {obs}")

# Use the loaded model to predict an action
action, _states = loaded_model.predict(obs, deterministic=True)
print(f"Predicted action: {action}")

# You can map the action index back to a meaningful name if you want
action_map = {0: 'increase_keyframe_rate', 1: 'decrease_keyframe_rate', 2: 'add_semantic_constraint'}
print(f"Predicted action name: {action_map[action]}")

# Clean up the environment
env.close()

print("\nScript finished successfully.")