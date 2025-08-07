# Feedback on Indexing Core RDDs

## RDD-IC-001: HNSW Parameter Tuning
*   **Assessment:** Approved. The recommendation to prioritize recall over latency is the correct one for our SLAM system.
*   **Next Steps:**
    *   The Indexing Core is now directed to update the `embedding_pipeline.py` script with the recommended HNSW parameters.

## RDD-IC-002: Hybrid Descriptor Strategy
*   **Assessment:** Approved. The recommendation to have the Pathfinder Guild conduct a thorough review of the SuperPoint and NetVLAD models is a good one.
*   **Next Steps:**
    *   The Pathfinder Guild is now directed to conduct a thorough review of the SuperPoint and NetVLAD papers and code repositories.
    *   The Indexing Core should await their findings before making a final recommendation.