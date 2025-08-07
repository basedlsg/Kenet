import json
import random

def load_ground_truth(filepath: str) -> list:
    """
    Loads the ground-truth dataset from a JSON file.

    Args:
        filepath: The path to the JSON file.

    Returns:
        A list of ground-truth entries.
    """
    with open(filepath, 'r') as f:
        return json.load(f)

def simulate_agent_proposals(ground_truth: list, agent_type: str) -> list:
    """
    Simulates constraint proposals from an agent.

    Args:
        ground_truth: The list of ground-truth constraints.
        agent_type: The type of agent ("Vanilla" or "Physics-Aware").

    Returns:
        A list of proposed constraints.
    """
    proposals = []
    for item in ground_truth:
        # The "Physics-Aware" agent is less likely to propose impossible constraints
        if agent_type == "Physics-Aware" and item["is_impossible"]:
            if random.random() > 0.8:  # Propose impossible constraint only 20% of the time
                proposals.append(item)
        # The "Vanilla" agent proposes constraints more freely
        elif agent_type == "Vanilla":
            if random.random() > 0.5: # Propose any given constraint 50% of the time
                proposals.append(item)
        else:
            if not item["is_impossible"]:
                proposals.append(item)


    return proposals

def calculate_icr(proposals: list) -> float:
    """
    Calculates the Impossible Constraint Rate (ICR).

    Args:
        proposals: A list of proposed constraints from an agent.

    Returns:
        The ICR as a float.
    """
    impossible_count = sum(1 for p in proposals if p["is_impossible"])
    total_proposals = len(proposals)
    if total_proposals == 0:
        return 0.0
    return impossible_count / total_proposals

def main():
    """
    Main function to run the ICR evaluation harness.
    """
    print("Running Impossible Constraint Rate (ICR) Evaluation Harness...")

    ground_truth_data = load_ground_truth("icr_ground_truth.json")

    # Simulate proposals for a "Vanilla" agent
    vanilla_proposals = simulate_agent_proposals(ground_truth_data, "Vanilla")
    vanilla_icr = calculate_icr(vanilla_proposals)
    print(f"\nVanilla Agent ICR: {vanilla_icr:.2f}")
    print(f"Total proposals: {len(vanilla_proposals)}")


    # Simulate proposals for a "Physics-Aware" agent
    physics_aware_proposals = simulate_agent_proposals(ground_truth_data, "Physics-Aware")
    physics_aware_icr = calculate_icr(physics_aware_proposals)
    print(f"Physics-Aware Agent ICR: {physics_aware_icr:.2f}")
    print(f"Total proposals: {len(physics_aware_proposals)}")


if __name__ == "__main__":
    main()