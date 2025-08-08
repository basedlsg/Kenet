# Implementation Plan: Advanced RAG Policies for SLAM
**Version:** 1.0
**Status:** In Draft
**Author:** Roo

---

## 1. Introduction for the Onboarding Developer

Welcome to the team! This document outlines the plan for implementing two advanced new features designed to significantly enhance our SLAM system's intelligence and performance. The goal is to move from static, rule-based systems to adaptive, learned policies.

This guide will provide you with the necessary context about our current project structure, our cloud environment, and a detailed, committee-driven plan to execute this initiative.

### 1.1. Project Context

*   **Local Repository:** The project is located on your local machine at `d:/oAI_1`.
*   **Git Repository:** The central code repository is hosted at `https://github.com/basedlsg/Kenet.git`.
*   **Key Files for This Task:**
    *   [`src/ppo_control_loop.py`](src/ppo_control_loop.py): The main entry point for the PPO-based reinforcement learning agent.
    *   [`src/slam_rag_loop.py`](src/slam_rag_loop.py): Contains the core logic for the Retrieval-Augmented Generation (RAG) pipeline.
    *   [`src/vector_db.py`](src/vector_db.py): A dedicated module for all interactions with our Qdrant vector database.
    *   [`atropos/`](atropos/): A newly cloned external library that provides a framework for asynchronous RL environments, which will be central to the "End-to-End RAG Policy" feature.

### 1.2. Cloud Environment Context

*   **Google Cloud Project:** All cloud resources for this project are under the GCP project ID `vertex-test-1-467818`.
*   **Authentication:** We use Application Default Credentials (ADC). The [`scripts/check_auth.py`](scripts/check_auth.py) script can be used to verify your connection.
*   **Core Services:**
    *   **Vertex AI:** We use this for hosting and querying the Gemini models for embedding generation and LLM-based verification.
    *   **Google Cloud Storage (GCS):** Used for storing datasets, model artifacts, and final trajectory outputs.

---

## 2. The Committee Structure

To ensure a high standard of quality, we will follow a committee-based approach for this implementation:

*   **Internal Code Committee:** Responsible for all local code implementation, from data processing and model architecture to integration.
*   **Cloud Committee:** Responsible for provisioning, configuring, and managing all cloud resources needed for training, hosting, and data storage.
*   **Documentation Committee:** Responsible for documenting the new features and ensuring the final report is clear and comprehensive.
*   **Review Committee:** Responsible for final review of all code and documentation to ensure accuracy, clarity, and adherence to best practices.

---

## 3. Feature 1: Learned Geometric Pruning

**Objective:** To replace our current fixed-distance geometric filter with a trained neural network that predicts the most likely regions for loop-closure candidates.

### 3.1. Internal Code Committee Tasks

1.  **Data Collection and Preparation:**
    *   **Action:** Modify the existing RL environment in [`src/atropos_env.py`](src/atropos_env.py) to log training data. For each step, we need to save a tuple containing `(query_embedding, query_3d_pose, positive_candidate_ids, negative_candidate_ids)`.
    *   **Location:** A new script, [`scripts/collect_pruning_data.py`](scripts/collect_pruning_data.py), will be created to run the environment and collect this data into a JSONL file.

2.  **Model Architecture:**
    *   **Action:** Create a new file for the pruning model. This will be a simple Multi-Layer Perceptron (MLP) built with PyTorch.
    *   **Location:** [`src/pruning_model.py`](src/pruning_model.py)
    *   **Details:** The MLP will take a concatenated vector of the query embedding and 3D pose as input, and output a probability score (using a sigmoid activation function) indicating the likelihood of finding a loop-closure candidate in a given region.

3.  **Model Training:**
    *   **Action:** Create a script to train the pruning model. This script will load the data collected in step 1, train the MLP, and save the trained model weights.
    *   **Location:** [`scripts/train_pruning_model.py`](scripts/train_pruning_model.py)

4.  **Integration into RAG Pipeline:**
    *   **Action:** Modify the `find_loop_closure_candidates` function in [`src/slam_rag_loop.py`](src/slam_rag_loop.py). Before querying the vector database, it will first load the trained pruning model and use it to predict the most promising regions to search. The vector search will then be filtered to only include these regions.
    *   **Location:** [`src/slam_rag_loop.py`](src/slam_rag_loop.py)

### 3.2. Cloud Committee Tasks

1.  **Data Storage:**
    *   **Action:** Create a new directory in our GCS bucket (`atropos_bucket`) to store the training data for the pruning model.
    *   **Location:** `gs://atropos_bucket/pruning_model_data/`

2.  **Model Training and Hosting:**
    *   **Action:** Set up a Vertex AI Training job to run the [`scripts/train_pruning_model.py`](scripts/train_pruning_model.py) script on a GPU-enabled instance.
    *   **Action:** Once the model is trained, register it in the Vertex AI Model Registry. This will allow us to version the model and easily deploy it to an endpoint for inference.

---

## 4. Feature 2: End-to-End Learned RAG Policy

**Objective:** To replace the separate "retrieve then verify" steps with a single, end-to-end policy network trained with reinforcement learning, using the `atropos` framework.

### 4.1. Internal Code Committee Tasks

1.  **Environment Implementation:**
    *   **Action:** The skeleton file for our new SLAM environment needs to be fully implemented. The `get_next_item` method must be updated to provide a realistic simulation of the SLAM system's state (e.g., current pose, sensor data). The `score` method must be updated to provide a meaningful reward signal based on the policy's performance.
    *   **Location:** [`atropos/environments/slam_env.py`](atropos/environments/slam_env.py)

2.  **Policy Network Architecture:**
    *   **Action:** Design and implement the policy network. This network will take the SLAM environment's state as input and output a joint distribution over all possible loop-closure candidates and a confidence score.
    *   **Location:** A new file, [`atropos/atroposlib/slam_policy_network.py`](atropos/atroposlib/slam_policy_network.py), will be created for this.

3.  **Trainer Implementation:**
    *   **Action:** The example training script needs to be updated to use the new `SLAMEnv` and the `RAGPolicy`. It will use the `Trainer` class from `atroposlib` to manage the RL training loop.
    *   **Location:** [`atropos/example_trainer/train_slam.py`](atropos/example_trainer/train_slam.py)

### 4.2. Cloud Committee Tasks

1.  **Inference Endpoints:**
    *   **Action:** The `APIServerConfig` in [`atropos/environments/slam_env.py`](atropos/environments/slam_env.py) currently points to a local server. For a production setup, this should be updated to point to a scalable inference solution. We will use Vertex AI Endpoints to host the policy model.
    *   **Location:** [`atropos/environments/slam_env.py`](atropos/environments/slam_env.py)

2.  **Distributed Training:**
    *   **Action:** To accelerate training, we will leverage `atropos`'s support for distributed data collection. This will involve setting up a Ray cluster on Google Kubernetes Engine (GKE) to run multiple instances of the `SLAMEnv` in parallel.
    *   **Location:** This will be a new GKE cluster in our GCP project.

---

## 5. Documentation and Review

*   **Documentation Committee:** As each feature is implemented, the `Project_Overview_and_Architecture.md` document should be updated with the new components and their interactions.
*   **Review Committee:** All new code will be submitted as a pull request to the `https://github.com/basedlsg/Kenet.git` repository and will require at least one approval from the Review Committee before being merged.
