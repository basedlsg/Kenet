import typing

def call_llm(prompt: str) -> str:
    """
    Placeholder for a real LLM API call.
    Simulates an LLM response based on keywords.
    """
    # Convert the prompt to lowercase to make keyword search case-insensitive
    # We look at the last line of the prompt which contains the constraint.
    last_line = prompt.strip().split('\n')[-2].lower()
    if "inside" in last_line or "floating" in last_line:
        return "impossible"
    else:
        return "valid"

def is_constraint_impossible(constraint: str) -> bool:
    """
    Uses a few-shot prompted LLM (simulated) to classify if a constraint is impossible.

    Args:
        constraint: The constraint string to be classified.

    Returns:
        True if the constraint is classified as "impossible", False otherwise.
    """
    prompt = f"""
You are an expert in robotics and 3D scene understanding. Your task is to classify a proposed scene layout constraint as "physically impossible" or "valid".

A "physically impossible" constraint is one that violates the laws of physics or common sense object interactions. For example, objects cannot occupy the same space as solid structures, and objects without support cannot hang in mid-air.

A "valid" constraint is one that is physically plausible, even if it's unusual.

Here are some examples:

---
Constraint: "the chair is inside the wall"
Classification: impossible
---
Constraint: "the monitor is floating in mid-air"
Classification: impossible
---
Constraint: "the desk is halfway through the floor"
Classification: impossible
---
Constraint: "the chair is on the floor next to the desk"
Classification: valid
---
Constraint: "the lamp is on the table"
Classification: valid
---
Constraint: "the keyboard is in front of the monitor on the desk"
Classification: valid
---

Now, classify the following constraint. Respond with only the word "impossible" or "valid".

Constraint: "{constraint}"
Classification:
"""
    response = call_llm(prompt)
    return response.strip().lower() == "impossible"

def main():
    """
    Main function to demonstrate the classifier.
    """
    print("Running Impossible Constraint Recognition (ICR) Automation Classifier...")

    sample_constraints = [
        "the chair is on the floor next to the desk",
        "the monitor is floating in mid-air",
        "the lamp is on the table",
        "the chair is inside the wall",
        "the mouse is on the mousepad",
        "the laptop is inside the closed drawer",
    ]

    print("\nClassifying sample constraints:")
    for constraint in sample_constraints:
        is_impossible = is_constraint_impossible(constraint)
        classification = "impossible" if is_impossible else "valid"
        print(f'- "{constraint}" -> {classification}')

if __name__ == "__main__":
    main()