import pickle
import numpy as np
from atropos_env import SLAMAtroposEnv
from tqdm import tqdm

# --- Configuration ---
# The project brief specifies 1,000,000 steps.
# For this sprint task, we'll collect 100,000 steps.
# TOTAL_STEPS = 1_000_000 # Target for final dataset
TOTAL_STEPS = 100_000
OUTPUT_FILE = "rollouts.pkl"
PROGRESS_INTERVAL = 100_000

def collect_rollouts():
    """
    Collects interaction roll-outs from the SLAMAtroposEnv using a random policy.
    """
    print("Initializing environment...")
    env = SLAMAtroposEnv()
    
    print(f"Collecting {TOTAL_STEPS} steps...")
    rollouts = []
    
    observation, _ = env.reset()
    
    # Use tqdm for a progress bar
    for step_num in tqdm(range(TOTAL_STEPS), desc="Collecting Rollouts"):
        # 1. Select an action based on the heuristic policy
        # If odometry drift is high, add a semantic constraint.
        odometry_drift = observation[1]
        if odometry_drift > 2.0:
            action = 2  # Action 2: add_semantic_constraint
        else:
            # Otherwise, randomly choose between the other actions (0 or 1).
            action = np.random.choice([0, 1])
        
        # 2. Execute the action in the environment
        next_observation, reward, terminated, truncated, info = env.step(action)
        
        # 3. Store the experience tuple
        rollouts.append((observation, action, reward, next_observation, terminated))
        
        # 4. Update observation
        observation = next_observation
        
        # 5. Reset if the episode is done
        if terminated or truncated:
            observation, _ = env.reset()
            
        # 6. Print progress (tqdm handles this, but we can add milestones)
        if (step_num + 1) % PROGRESS_INTERVAL == 0:
            print(f"\nMilestone: Reached {step_num + 1} steps.")

    print(f"\nCollection complete. Total rollouts collected: {len(rollouts)}")
    
    # --- Save the data ---
    print(f"Saving rollouts to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(rollouts, f)
        
    print("Save complete.")

if __name__ == "__main__":
    collect_rollouts()