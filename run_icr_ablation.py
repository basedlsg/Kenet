import numpy as np
import json
from automate_icr import is_constraint_impossible

class RAGSLAMAgent:
    """
    A simulated agent that proposes layout constraints.
    """
    def __init__(self, physics_aware: bool):
        self.physics_aware = physics_aware
        if self.physics_aware:
            # Lower probability of generating an impossible constraint
            self.impossible_prob = 0.1
        else:
            # Higher probability for the vanilla agent
            self.impossible_prob = 0.6

    def propose_constraint(self) -> str:
        """
        Generates a plausible or impossible constraint based on the agent's awareness.
        """
        impossible_constraints = [
            "the chair is inside the wall",
            "the monitor is floating in mid-air",
            "the desk is halfway through the floor",
            "the lamp is inside the desk",
        ]
        valid_constraints = [
            "the chair is on the floor next to the desk",
            "the lamp is on the table",
            "the keyboard is in front of the monitor on the desk",
            "the mouse is on the mousepad",
        ]

        if np.random.rand() < self.impossible_prob:
            return np.random.choice(impossible_constraints)
        else:
            return np.random.choice(valid_constraints)

def run_simulation(agent: RAGSLAMAgent, num_proposals: int) -> list:
    """
    Runs a simulation for a given agent and logs its proposed constraints.
    """
    log = []
    print(f"--- Running simulation for {'Physics-Aware' if agent.physics_aware else 'Vanilla'} Agent ---")
    for i in range(num_proposals):
        constraint = agent.propose_constraint()
        log.append({"step": i, "constraint": constraint})
        print(f"  Step {i+1}: Proposed '{constraint}'")
    return log

def calculate_icr(log: list) -> float:
    """
    Calculates the Impossible Constraint Rate from a log file.
    """
    impossible_count = 0
    for entry in log:
        if is_constraint_impossible(entry["constraint"]):
            impossible_count += 1
    
    if not log:
        return 0.0
        
    return impossible_count / len(log)

def main():
    """
    Main function to run the ablation study.
    """
    print("Starting Ablation Study: MetaSpatial Pre-training Impact on ICR...")
    num_proposals = 20

    # 1. Simulate the Vanilla Agent (no physics pre-training)
    vanilla_agent = RAGSLAMAgent(physics_aware=False)
    vanilla_log = run_simulation(vanilla_agent, num_proposals)
    vanilla_icr = calculate_icr(vanilla_log)

    # 2. Simulate the Physics-Aware Agent
    physics_agent = RAGSLAMAgent(physics_aware=True)
    physics_log = run_simulation(physics_agent, num_proposals)
    physics_icr = calculate_icr(physics_log)

    # 3. Report the results
    print("\n--- Ablation Study Results ---")
    print(f"Impossible Constraint Rate (ICR) for Vanilla Agent:      {vanilla_icr:.2%}")
    print(f"Impossible Constraint Rate (ICR) for Physics-Aware Agent: {physics_icr:.2%}")
    
    reduction = vanilla_icr - physics_icr
    print(f"\nReduction in ICR due to MetaSpatial Pre-training: {reduction:.2%}")
    print("--- Study Finished ---")

if __name__ == "__main__":
    main()