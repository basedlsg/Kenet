# RDD-CG-001: Profiling and Observability Framework

## 1.0 Introduction
This document addresses the first key question for the Code Guardians: "What profiling tools should be integrated into the main loop to measure the latency of each SLam stage?"

## 2.0 Analysis of the Options
We have identified three main options for our profiling and observability framework:

*   **`cProfile`:** The built-in profiler for Python.
*   **`Py-spy`:** A sampling profiler with a very low overhead.
*   **`Scalene`:** A high-performance CPU and memory profiler.

## 3.0 Recommendation
We recommend that we use **`Scalene`** for our project. It provides the best combination of performance, accuracy, and features.

## 4.0 Next Steps
*   The Code Guardians will now proceed to the second key question: "What is the optimal CI/CD workflow for a project involving both Python code and ML model training?"