import os
import sys
from google.cloud import storage

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python upload_file.py <bucket_name> <source_file_path> <destination_blob_name>")
        sys.exit(1)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/carlos/.config/gcloud/application_default_credentials.json"
    bucket_name = sys.argv[1]
    source_file_path = sys.argv[2]
    destination_blob_name = sys.argv[3]

    if not os.path.isfile(source_file_path):
        print(f"Error: Source file not found at '{source_file_path}'")
        sys.exit(1)

    upload_to_gcs(bucket_name, source_file_path, destination_blob_name)