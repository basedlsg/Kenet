# RDD-BPCQ-2: A New File Modification Protocol

## 1.0 Introduction
*   **1.1: Problem Statement:** The file modification tools, `apply_diff` and `write_to_file`, are experiencing persistent failures. This is due to a state drift between the agent's internal representation of the file and the file system. The existing "File Modification Protocol" outlined in the `PROJECT_ATROPOS_MASTER_PLAN.md` is not being consistently followed, leading to these errors.
*   **1.2: Scope:** This RDD will propose a new, more robust file modification protocol that eliminates the possibility of state drift errors. This will involve a survey of alternative file modification tools and libraries, and a recommendation for a new protocol that is both reliable and easy to follow.
*   **1.3: Success Metrics:**
    *   **File Modification Success Rate:** >99.9%
    *   **Reduction in Manual Intervention:** Reduce the need for manual correction of file modification errors by 100%.
    *   **Adherence to Protocol:** 100% of file modification operations must follow the new protocol.

## 2.0 Analysis of the Options
*   **2.1: Option 1: `python-patch` library:** This is a lightweight, dependency-free library for parsing and applying unified diffs. It automatically handles line ending conversions and can detect patch formats from SVN, HG, and Git.
*   **2.2: Option 2: Python's built-in `difflib` module:** This module is part of the Python standard library and provides tools for comparing sequences. It can be used to generate diffs in various formats, including unified diffs, which can then be applied.
*   **2.3: Option 3: `GitPython` library:** This is a comprehensive library for interacting with Git repositories. It can be used to generate diffs, but it may be too heavyweight for our purposes, as we only need to apply diffs, not interact with a full Git repository.

## 3.0 Recommendation
*   **3.1: Recommended Option:** A new, two-tiered file modification protocol that prioritizes safety and reliability. This protocol will replace the existing, error-prone `apply_diff` and `write_to_file` tools with a new set of tools that are more robust and less susceptible to state drift errors.
    *   **Tier 1: `safe_apply_diff`:** This tool will be the primary method for making small, targeted changes to files. It will automatically read the file from disk before applying the diff, and it will use the `python-patch` library to apply the diff.
    *   **Tier 2: `safe_write_to_file`:** This tool will be used for creating new files or for making large-scale changes to existing files. It will create a backup of the original file before writing the new content, and it will automatically restore the backup if the write operation fails.
*   **3.2: Trade-offs:** This new protocol will be slightly slower than the existing protocol, as it requires an extra read operation before each write. However, this is a small price to pay for the increased reliability and safety that it provides.

## 4.0 Next Steps
*   **4.1: Action Items:**
    *   **Phase 2 (Design & Prototyping):**
        *   Create a detailed technical design for the `safe_apply_diff` and `safe_write_to_file` tools.
        *   Develop a prototype of the new tools and test them against a suite of file modification scenarios.
    *   **Phase 3 (Implementation & Integration):**
        *   Implement the new tools and integrate them into the development environment.
        *   Deprecate the old `apply_diff` and `write_to_file` tools.
    *   **Phase 4 (Verification & Finalization):**
        *   Verify that the new tools meet the success metrics defined in this RDD.
        *   Update the `PROJECT_ATROPOS_MASTER_PLAN.md` to reflect the new protocol.