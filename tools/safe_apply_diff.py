import patch
import sys
from safe_write_to_file import safe_write_to_file

def safe_apply_diff(file_path, diff_str):
    """
    Applies a diff to a file in a safe manner.
    """
    try:
        # Read the file from disk
        with open(file_path, "r") as f:
            original_content = f.read()

        # Apply the diff
        patched_content = patch.from_string(diff_str).apply(original_content)

        # Write the modified file to disk using the safe_write_to_file tool
        if safe_write_to_file(file_path, patched_content):
            return True
        else:
            return False

    except Exception as e:
        print(f"Error applying diff: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python safe_apply_diff.py <file_path> <diff_str>")
        sys.exit(1)

    file_path = sys.argv
    diff_str = sys.argv

    if safe_apply_diff(file_path, diff_str):
        print("Diff applied successfully.")
    else:
        print("Failed to apply diff.")