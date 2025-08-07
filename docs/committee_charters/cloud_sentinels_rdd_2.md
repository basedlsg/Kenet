# RDD-CS-002: Fine-Tuning for Verification

## 1.0 Introduction
This document addresses the second key question for the Cloud Sentinels: "Is it feasible and cost-effective to fine-tune a smaller, specialized model on Vertex AI for the loop closure verification task, replacing `gemini-1.5-flash`?"

## 2.0 Analysis of the Options
We have identified two main options for our verification model:

*   **`gemini-1.5-flash`:** A large, general-purpose model that is expensive to run.
*   **A smaller, fine-tuned model:** A smaller, specialized model that is less expensive to run, but requires an initial investment in fine-tuning.

## 3.0 Cost-Benefit Analysis
Based on a review of the Vertex AI pricing page, we have determined that the cost of fine-tuning a smaller model is based on the number of "node hours" required for the training job. The exact cost will depend on the size of the model and the amount of training data.

## 4.0 Recommendation
We recommend that we proceed with a proof-of-concept to fine-tune a smaller model on Vertex AI. This will allow us to gather more accurate data on the cost and performance of the fine-tuned model, and to make a more informed decision about whether to adopt this approach in the long run.

## 5.0 Next Steps
*   The Cloud Sentinels will work with the Pathfinder Guild to select a candidate model for fine-tuning.
*   The Cloud Sentinels will then create a proof-of-concept to fine-tune the model on Vertex AI.