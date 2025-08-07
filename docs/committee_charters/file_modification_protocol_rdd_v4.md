# RDD-BPCQ-4: A New File Modification Protocol

## 1.0 Introduction
*   **1.1: Problem Statement:** The file modification tools, `apply_diff` and `write_to_file`, are experiencing persistent failures. This is due to a state drift between the agent's internal representation of the file and the file system. The existing "File Modification Protocol" outlined in the `PROJECT_ATROPOS_MASTER_PLAN.md` is not being consistently followed, leading to these errors. The previously developed `safe_apply_diff` and `safe_write_to_file` tools are not being utilized.
*   **1.2: Scope:** This RDD will propose a new, more robust file modification protocol that eliminates the possibility of state drift errors. This will involve the deprecation of the old `apply_diff` and `write_to_file` tools and the exclusive use of the new, safer tools.
*   **1.3: Success Metrics:**
    *   **File Modification Success Rate:** >99.9%
    *   **Reduction in Manual Intervention:** Reduce the need for manual correction of file modification errors by 100%.
    *   **Adherence to Protocol:** 100% of file modification operations must follow the new protocol.

## 2.0 Analysis of the Options
*   **2.1: Option 1: Continue with the existing protocol:** This is not a viable option, as it has been proven to be unreliable.
*   **2.2: Option 2: Enforce the use of the `safe_apply_diff` and `safe_write_to_file` tools:** This is the recommended option. The tools have already been developed and tested, and they have been shown to be effective in preventing state drift errors.

## 3.0 Recommendation
*   **3.1: Recommended Option:** A new, two-tiered file modification protocol that prioritizes safety and reliability. This protocol will replace the existing, error-prone `apply_diff` and `write_to_file` tools with the new `safe_apply_diff` and `safe_write_to_file` tools.
    *   **Tier 1: `safe_apply_diff`:** This tool will be the primary method for making small, targeted changes to files. It will automatically read the file from disk before applying the diff, and it will use the `python-patch` library to apply the diff.
    *   **Tier 2: `safe_write_to_file`:** This tool will be used for creating new files or for making large-scale changes to existing files. It will create a backup of the original file before writing the new content, and it will automatically restore the backup if the write operation fails.
*   **3.2: Trade-offs:** This new protocol will be slightly slower than the existing protocol, as it requires an extra read operation before each write. However, this is a small price to pay for the increased reliability and safety that it provides.

## 4.0 Next Steps
*   **4.1: Action Items:**
    *   **Phase 2 (Implementation & Integration):**
        *   Integrate the `safe_apply_diff` and `safe_write_to_file` tools into the agent's toolset.
        *   Deprecate the old `apply_diff` and `write_to_file` tools.
    *   **Phase 3 (Verification & Finalization):**
        *   Verify that the new tools meet the success metrics defined in this RDD.
        *   Update the `PROJECT_ATROPOS_MASTER_PLAN.md` to reflect the new protocol.