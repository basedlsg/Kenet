# File Modification Protocol

## 1.0 Introduction
This document outlines the protocol for modifying files in the Project Atropos. This protocol is designed to prevent state drift and to ensure that file modification operations are performed in a reliable and predictable manner.

## 2.0 Protocol
1.  **Read Before Write:** Before any file modification operation (`apply_diff` or `write_to_file`), the committee must first read the file using the `read_file` tool to ensure its internal representation is in sync with the file system.
2.  **Use `apply_diff` for Small, Targeted Changes:** The `apply_diff` tool should only be used for small, targeted changes to existing code. If the change is larger than a few lines, or if it involves multiple sections of the file, then the `write_to_file` tool should be used instead.
3.  **Use `write_to_file` for Large Changes and New Files:** The `write_to_file` tool should be used for large changes to existing files, and for creating new files.
4.  **Pivot After Two Failures:** If a file modification operation fails more than twice, the committee must immediately pivot to a different approach. This may involve using a different tool, or it may involve rethinking the problem and coming up with a different solution.
5.  **Consult with Other Committees:** If a committee is unable to find a viable alternative approach on its own, it should formally consult with other committees to brainstorm new solutions.