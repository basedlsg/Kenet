# Committee Charter: The Pathfinder Guild (Research & Development)

## Mandate
To survey the state-of-the-art in robotics, AI, and software engineering to provide the project with external intelligence, identifying novel techniques and reusable assets.

## Phase 1 Directives

### 1. Initial Key Questions (Due: EOD 2025-08-13)
Your first task is to produce a Research & Design Document (RDD) that provides definitive answers to the following questions:

*   **1.1: Alternative Verification Models:** What are the current state-of-the-art alternatives to the `gemini-1.5-flash` verification model for loop closure? Your analysis must include:
    *   A survey of at least three smaller, specialized models (e.g., classification heads, fine-tuned models).
    *   A quantitative comparison of their accuracy, latency, and cost per verification.
    *   A recommendation for the best model to prototype.

*   **1.2: Geometric Pruning Libraries:** Can we identify any open-source `gtsam` integration libraries or geometric verification modules that meet our quality standards? Your analysis must include:
    *   A review of at least two relevant Git repositories.
    *   A quality score for each repository based on the rubric defined in the Master Plan (code quality, documentation, license, performance).
    *   A recommendation on whether to adopt an external library or build a custom solution.

### 2. Collaboration Protocol
*   You are required to hold a kickoff meeting with the **RAG & Vector Systems Committee** to align on the requirements for the geometric pruning and verification models.
*   You must consult with the **Best Practices & Code Quality Committee** to ensure your repository vetting process aligns with the project's engineering standards.

All findings and recommendations must be submitted as a formal RDD to the Oversight Committee for review.