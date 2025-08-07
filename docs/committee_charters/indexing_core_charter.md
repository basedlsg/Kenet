# Committee Charter: The Indexing Core (RAG & Vector Systems)

## Mandate
To own the entire Retrieval-Augmented Generation pipeline, from embedding generation to vector search and indexing. This committee is responsible for the speed and accuracy of the semantic search component.

## Phase 1 Directives

### 1. Initial Key Questions (Due: EOD 2025-08-13)
Your first task is to produce a Research & Design Document (RDD) that provides definitive answers to the following questions:

*   **1.1: Optimal HNSW Parameters:** What are the optimal HNSW parameters (`M`, `efConstruction`, `efSearch`) for our dataset and latency requirements? Your analysis must include:
    *   A description of the methodology used to determine the optimal parameters.
    *   Empirical results from benchmark tests showing the trade-offs between recall and query latency.
    *   A final recommendation for the production settings.

*   **1.2: Hybrid Descriptor Strategy:** What is the most effective strategy for combining Gemini embeddings with a geometric descriptor like SuperPoint or NetVLAD? Your RDD should include:
    *   A survey of at least two different fusion techniques (e.g., concatenation, weighted averaging).
    *   A prototype implementation of the recommended fusion technique.
    *   Benchmark results comparing the performance of the hybrid descriptor against the pure semantic embedding.

### 2. Collaboration Protocol
*   You are required to hold a kickoff meeting with the **Pathfinder Guild** to provide your requirements for the geometric pruning and verification models.
*   You must consult with the **Cloud Sentinels** to understand the cost and performance implications of your proposed solutions.

All findings and recommendations must be submitted as a formal RDD to the Oversight Committee for review.