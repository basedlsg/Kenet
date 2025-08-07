import os
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError

def check_adc():
    """Checks for Application Default Credentials and prints their status."""
    try:
        credentials, project_id = default()
        print("Application Default Credentials (ADC) are set up correctly.")
        print(f"Project ID from credentials: {project_id}")
        
        # Check for the ADC file path
        adc_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if adc_path:
            print(f"ADC file path is set to: {adc_path}")
        else:
            # On Windows, the file is typically here:
            gcloud_config_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "gcloud", "application_default_credentials.json")
            if os.path.exists(gcloud_config_path):
                print(f"Found ADC file at the default location: {gcloud_config_path}")
            else:
                print("Warning: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set, and no ADC file was found in the default location.")

    except DefaultCredentialsError:
        print("Error: Application Default Credentials (ADC) not found.")
        print("Please run 'gcloud auth application-default login' in your terminal to set them up.")

if __name__ == "__main__":
    check_adc()