# RDD-PA-002: SLAM Experimentation MCP

## 1.0 Introduction
This document addresses the second key question for the Protocol Architects: "What would an MCP for running a full SLAM experiment and returning a performance report look like?"

## 2.0 Design
We propose to create an MCP server that provides the following tools:

*   **`run_experiment`:** This tool will trigger a new SLAM evaluation run. It will take a single argument, `config`, which will be a JSON object that specifies the parameters for the experiment.
*   **`get_results`:** This tool will retrieve the results of a previous experiment. It will take a single argument, `experiment_id`, which will be the ID of the experiment to retrieve.

The `config` object will have the following structure:

```json
{
  "mode": "rag-slam",
  "output": "trajectory.txt",
  "gcs_bucket": "atropos_bucket"
}
```

The `get_results` tool will return a JSON object with the following structure:

```json
{
  "experiment_id": "12345",
  "status": "complete",
  "results": {
    "ate": 0.123,
    "rpe": 0.456
  }
}
```

## 3.0 Next Steps
*   The Protocol Architects will now proceed to the next phase of the project, which is to implement the SLAM experimentation MCP.