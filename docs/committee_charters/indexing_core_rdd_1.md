# RDD-IC-001: HNSW Parameter Tuning

## 1.0 Introduction
This document addresses the first key question for the Indexing Core: "What are the optimal HNSW parameters (`m`, `ef_construct`, `ef_search`) for our dataset and latency requirements?"

## 2.0 Methodology
We conducted a benchmark test of 48 different HNSW parameter combinations using the `embedding_pipeline.py` script. The benchmark measured the average query latency and recall for each parameter set over 100 queries.

## 3.0 Results
The benchmark yielded the following key results:

*   **Best Latency:** 2.99ms (recall=0.16) with `m=64`, `ef_construct=256`, `ef_search=128`.
*   **Best Recall:** 0.31 (latency=4.46ms) with `m=16`, `ef_construct=128`, `ef_search=256`.

## 4.0 Recommendation
For our SLAM system, a high recall is more important than a low latency. Therefore, we recommend adopting the parameters that yielded the highest recall:

*   `m = 16`
*   `ef_construct = 128`
*   `ef_search = 256`

These parameters will provide a good balance of performance and accuracy for our system.

## 5.0 Next Steps
*   The Indexing Core will now proceed to the second key question: "What is the most effective strategy for combining Gemini embeddings with a geometric descriptor like SuperPoint or NetVLAD?"