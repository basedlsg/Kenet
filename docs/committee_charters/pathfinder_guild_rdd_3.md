# RDD-Pathfinder-3: Loop Closure Verification Model Selection

## 1.0 Introduction
*   **1.1: Problem Statement:** The current SLAM system relies on a placeholder model (`gemini-1.5-flash`) for loop closure verification. This is not a long-term solution, and a more specialized, efficient, and accurate model is needed to improve the performance and reduce the cost of the system.
*   **1.2: Scope:** This RDD will evaluate four options for the loop closure verification model: the existing MobileNetV2 prototype, the `gemini-1.5-flash` model, a MixVPR/LightGlue-based model, and an unsupervised autoencoder-based model. The evaluation will include a comparison of performance, cost, and ease of integration.
*   **1.3: Success Metrics:**
    *   **Accuracy:** The model should achieve a loop closure verification accuracy of >95% on a benchmark dataset.
    *   **Latency:** The model should have a p99 query latency of < 50ms.
    *   **Cost:** The cost per 1000 loop closures should be reduced by >50% compared to the current `gemini-1.5-flash` model.

## 2.0 Analysis of the Options
*   **2.1: Option 1: MobileNetV2 Prototype:** A detailed analysis of the existing MobileNetV2 prototype, including its performance, cost, and ease of integration.
*   **2.2: Option 2: `gemini-1.5-flash` Model:** A detailed analysis of the `gemini-1.5-flash` model, including its performance, cost, and ease of integration.
*   **2.3: Option 3: MixVPR/LightGlue-based Model:** This approach, based on the paper "A Robust and Lightweight Loop Closure Detection Approach for Challenging Environments," uses a combination of MixVPR for global descriptors, SuperPoint for local feature extraction, and LightGlue for feature matching. The paper claims this approach is robust in challenging environments and has been evaluated on public datasets. The use of TensorRT for accelerating model inference is also mentioned, which could help in achieving the latency and cost success metrics.
*   **2.4: Option 4: Unsupervised Autoencoder-based Model:** This approach, based on the paper "Lightweight Unsupervised Deep Loop Closure," proposes an unsupervised deep neural network based on a denoising autoencoder architecture. The model is trained to be robust to viewpoint changes by warping images with randomized projective transformations and uses Histogram of Oriented Gradients (HOG) descriptors to improve robustness to illumination changes. A GitHub repository with the code for this paper is available, which will be useful for implementation and benchmarking.

## 3.0 Recommendation
*   **3.1: Recommended Option:** The recommended option, with a clear justification for why it was chosen.
*   **3.2: Trade-offs:** The trade-offs of the recommended option.

## 4.0 Next Steps
*   **4.1: Action Items:**
    *   Benchmark the MobileNetV2 prototype against the `gemini-1.5-flash` model.
    *   Implement and benchmark the MixVPR/LightGlue-based model.
    *   Implement and benchmark the unsupervised autoencoder-based model.
    *   Investigate open-source gtsam integration libraries.
    *   Draft the final RDD document summarizing findings.
    *   Submit RDD for review.