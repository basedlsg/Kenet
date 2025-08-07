import gymnasium as gym
from gymnasium import spaces
import numpy as np

class SLAMAtroposEnv(gym.Env):
    """
    A simulated Reinforcement Learning environment for a SLAM agent
    based on the Atropos framework.
    """
    def __init__(self, env_config=None):
        super(SLAMAtroposEnv, self).__init__()

        # --- Define Spaces ---
        # Observation Space: [tracking_fps, odometry_drift, keypoints_matched, loop_closure_score, semantic_similarity_mean]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0.0, 0.0]),
            high=np.array([120, 1000, 500, 1.0, 1.0]),
            dtype=np.float32
        )

        # Action Space: Discrete actions the LLM can take.
        # 0: 'increase_keyframe_rate'
        # 1: 'decrease_keyframe_rate'
        # 2: 'add_semantic_constraint'
        self.action_space = spaces.Discrete(3)

        # --- Environment State ---
        self.current_fps = 30.0
        self.current_drift = 1.0
        self.keypoints_matched = 50
        self.loop_closure_score = 0.1
        self.semantic_similarity_mean = 0.2
        self.target_fps = 60.0
        self.step_count = 0
        self.max_steps = 100 # Terminate after a certain number of steps

    def reset(self, seed=None, options=None):
        """
        Resets the environment to its initial state.
        """
        super().reset(seed=seed)
        
        # Reset state variables
        self.current_fps = 30.0
        self.current_drift = 1.0
        self.keypoints_matched = 50
        self.loop_closure_score = 0.1
        self.semantic_similarity_mean = 0.2
        self.step_count = 0

        # Return initial observation
        observation = np.array([
            self.current_fps,
            self.current_drift,
            self.keypoints_matched,
            self.loop_closure_score,
            self.semantic_similarity_mean
        ], dtype=np.float32)
        info = {}
        return observation, info

    def step(self, action):
        """
        Executes one time step within the environment.
        """
        self.step_count += 1

        # --- Simulate Action Effect ---
        if action == 0:  # increase_keyframe_rate
            self.current_fps -= 5
            self.current_drift -= 0.1
            self.keypoints_matched += 20 # More keyframes, more matches
        elif action == 1:  # decrease_keyframe_rate
            self.current_fps += 5
            self.current_drift += 0.15
            self.keypoints_matched -= 20 # Fewer keyframes, fewer matches
        elif action == 2:  # add_semantic_constraint
            self.current_fps -= 2
            self.current_drift -= 0.25
            self.loop_closure_score += 0.2 # Semantic constraints improve loop closure
            self.semantic_similarity_mean += 0.15 # And semantic similarity

        # --- Simulate environmental noise/drift ---
        self.current_drift += np.random.normal(0.0, 0.05)
        self.loop_closure_score *= 0.98 # Decay over time
        self.semantic_similarity_mean *= 0.99 # Decay over time


        # Ensure values stay within reasonable bounds
        self.current_fps = np.clip(self.current_fps, 0, 120)
        self.current_drift = max(0, self.current_drift)
        self.keypoints_matched = np.clip(self.keypoints_matched, 0, 500)
        self.loop_closure_score = np.clip(self.loop_closure_score, 0.0, 1.0)
        self.semantic_similarity_mean = np.clip(self.semantic_similarity_mean, 0.0, 1.0)

        # --- Calculate Reward ---
        lambda_constant = 0.2
        reward = -self.current_drift - (lambda_constant / (self.current_fps + 1e-6)) # Add epsilon to avoid division by zero

        # --- Check for Termination ---
        terminated = self.step_count >= self.max_steps

        # --- Prepare Return Values ---
        next_observation = np.array([
            self.current_fps,
            self.current_drift,
            self.keypoints_matched,
            self.loop_closure_score,
            self.semantic_similarity_mean
        ], dtype=np.float32)
        info = {}

        return next_observation, reward, terminated, False, info

    def render(self):
        """
        Render the environment.
        """
        pass

    def close(self):
        """
        Clean up the environment.
        """
        pass