import os

def set_gcs_credentials():
    """
    Sets the GOOGLE_APPLICATION_CREDENTIALS environment variable.
    """
    credential_path = "/Users/carlos/NOUS/secure_keys/gcp_credentials.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path
    print(f"GOOGLE_APPLICATION_CREDENTIALS set to: {credential_path}")

if __name__ == "__main__":
    set_gcs_credentials()