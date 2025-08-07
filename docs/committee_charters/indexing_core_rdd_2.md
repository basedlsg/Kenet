# RDD-IC-002: Hybrid Descriptor Strategy

## 1.0 Introduction
This document addresses the second key question for the Indexing Core: "What is the most effective strategy for combining Gemini embeddings with a geometric descriptor like SuperPoint or NetVLAD?"

## 2.0 Analysis of the Bottleneck
The current implementation uses only semantic embeddings for loop closure detection. This can lead to false positives, as two different locations can have similar captions.

## 3.0 Proposed Solution
We propose to create a hybrid descriptor by combining our existing Gemini embeddings with a geometric descriptor. Based on a web search, we have identified two promising candidates for the geometric descriptor:

*   **SuperPoint:** A self-supervised framework for training interest point detectors and descriptors.
*   **NetVLAD:** A neural network architecture for place recognition.

## 4.0 Recommendations
Without being able to browse the papers and code repositories, we cannot provide a more detailed recommendation. Therefore, we recommend that the **Pathfinder Guild** conduct a thorough review of the SuperPoint and NetVLAD papers and code repositories as their next task. This review should include:

*   A detailed analysis of the models and their performance.
*   A recommendation on which model to use for our SLAM system.
*   A proposal for how to integrate the chosen model into our existing pipeline.

## 5.0 Next Steps
*   The Pathfinder Guild should begin their review of the SuperPoint and NetVLAD papers and code repositories immediately.
*   The Indexing Core will await their findings before making a final recommendation.