# Committee Charter: The Cloud Sentinels (Google Cloud & AI Services)

## Mandate
To manage all interactions with Google Cloud services, focusing on cost optimization, security, and the strategic use of Vertex AI.

## Phase 1 Directives

### 1. Initial Key Questions (Due: EOD 2025-08-13)
Your first task is to produce a Research & Design Document (RDD) that provides definitive answers to the following questions:

*   **1.1: Managed vs. Self-Hosted Vector DB:** Should we use Vertex AI Matching Engine instead of a self-managed Qdrant instance? Your analysis must include:
    *   A detailed cost-benefit analysis, including infrastructure, maintenance, and API costs.
    *   A performance comparison, including query latency and indexing speed.
    *   A recommendation for the best solution for our project.

*   **1.2: Fine-Tuning for Verification:** Is it feasible and cost-effective to fine-tune a smaller, specialized model on Vertex AI for the loop closure verification task, replacing `gemini-1.5-flash`? Your RDD should include:
    *   A cost estimate for the fine-tuning process.
    *   A performance projection for the fine-tuned model (accuracy, latency, and cost per verification).
    *   A recommendation on whether to proceed with fine-tuning.

### 2. Collaboration Protocol
*   You are required to hold a kickoff meeting with the **Indexing Core** to understand their requirements for the vector database and verification model.
*   You must consult with the **Best Practices Guardians** to ensure your proposed solutions are compliant with the project's security and infrastructure standards.

All findings and recommendations must be submitted as a formal RDD to the Oversight Committee for review.