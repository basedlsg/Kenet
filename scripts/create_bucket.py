import argparse
from google.cloud import storage
from google.api_core import exceptions

def create_gcs_bucket(bucket_name, project_id, location):
    """Creates a new GCS bucket."""
    try:
        storage_client = storage.Client(project=project_id)
        bucket = storage_client.create_bucket(bucket_name, location=location)
        print(f"Bucket {bucket.name} created in {bucket.location} for project {bucket.project_number}.")
        return True
    except exceptions.Conflict:
        print(f"Bucket {bucket_name} already exists.")
        return True # It already exists, so we can proceed.
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure you have the correct permissions and that you have authenticated with Google Cloud by running 'gcloud auth application-default login'.")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a GCS bucket.")
    parser.add_argument("bucket_name", type=str, help="The name for the new bucket.")
    parser.add_argument("project_id", type=str, help="The Google Cloud project ID.")
    parser.add_argument("location", type=str, help="The location for the bucket (e.g., us-central1).")
    args = parser.parse_args()

    create_gcs_bucket(args.bucket_name, args.project_id, args.location)