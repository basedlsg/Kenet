# Folder Structure Proposal

## 1. Analysis of the Current Structure

The current project folder structure has several issues that hinder development and organization:

*   **Flat Hierarchy:** A large number of files are located in the root directory, making it difficult to locate specific files and understand the project's architecture.
*   **Inconsistent Naming:** The `committee_charters` directory contains files with inconsistent naming conventions (e.g., `_feedback_1`, `_rdd_1`).
*   **Lack of Separation of Concerns:** Source code, documentation, data, and scripts are mixed, leading to a cluttered and confusing workspace.
*   **No Dedicated Data Directory:** Critical data files like `icr_ground_truth.json` are in the root directory, which is not ideal for data management.

## 2. Proposed Folder Structure

To address these issues, I propose the following folder structure:

```
/
├── data/
│   ├── icr_ground_truth.json
│   └── ... (other data files)
├── docs/
│   ├── committee_charters/
│   │   └── ... (all charter files)
│   ├── PROJECT_ATROPOS_MASTER_PLAN.md
│   └── ... (all other .md files)
├── notebooks/
│   └── prototypes/
│       └── ... (all prototype files)
├── scripts/
│   ├── automate_icr.py
│   ├── calculate_ate.py
│   ├── check_auth.py
│   ├── collect_rollouts.py
│   ├── configure_secrets.py
│   ├── create_bucket.py
│   ├── create_noisy_trajectory.py
│   ├── download_dataset.py
│   ├── download_nyu_depth_v2.py
│   ├── generate_captions.py
│   ├── generate_metaspatial_dataset.py
│   ├── run_icr_ablation.py
│   └── upload_file.py
├── src/
│   ├── __init__.py
│   ├── atropos_env.py
│   ├── embedding_pipeline.py
│   ├── gcs_auth.py
│   ├── ppo_control_loop.py
│   ├── slam_rag_loop.py
│   └── train_ppo.py
├── tools/
│   ├── safe_apply_diff.py
│   └── safe_write_to_file.py
├── results/
│   ├── ppo_slam_tensorboard/
│   │   └── ...
│   └── ppo_slam_agent.zip
└── .gitignore
```

### Rationale for Changes

*   **`data/`**: A dedicated directory for all raw and processed data.
*   **`docs/`**: All markdown files and documentation, including the `committee_charters`, will be consolidated here.
*   **`notebooks/`**: For Jupyter notebooks and experimental code, including the existing `prototypes`.
*   **`scripts/`**: All standalone scripts for various tasks.
*   **`src/`**: The main source code of the project.
*   **`tools/`**: Project-specific tools and utilities.
*   **`results/`**: For storing the output of models and experiments, like TensorBoard logs and trained models.

## 3. Migration Plan

1.  **Create the new directories:** `data`, `docs`, `notebooks`, `scripts`, `src`, `tools`, and `results`.
2.  **Move files to their new locations** according to the proposed structure.
3.  **Update any hardcoded paths** in the scripts and code to reflect the new structure.
4.  **Delete the old, now-empty directories.**

This new structure will provide a cleaner, more organized, and scalable foundation for the project.