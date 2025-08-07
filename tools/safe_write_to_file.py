import os
import sys

def safe_write_to_file(file_path, content):
    """
    Writes content to a file in a safe manner using a temporary file and atomic rename.
    """
    temp_path = file_path + ".tmp"
    backup_path = file_path + ".bak"
    try:
        # Create a backup of the original file if it exists
        if os.path.exists(file_path):
            os.rename(file_path, backup_path)

        # Write the new content to a temporary file
        with open(temp_path, "w") as f:
            f.write(content)

        # Atomically rename the temporary file to the final destination
        os.rename(temp_path, file_path)

        # Remove the backup file on success
        if os.path.exists(backup_path):
            os.remove(backup_path)

        return True
    except Exception as e:
        print(f"Error writing to file: {e}")
        # Attempt to restore the backup if the write operation fails
        if os.path.exists(backup_path):
            os.rename(backup_path, file_path)
        # Clean up the temporary file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python safe_write_to_file.py <file_path> <content>")
        sys.exit(1)

    file_path = sys.argv
    content = sys.argv

    if safe_write_to_file(file_path, content):
        print("File written successfully.")
    else:
        print("Failed to write to file.")