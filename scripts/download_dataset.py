import os
import requests
import tarfile
from tqdm import tqdm

def download_file(url, local_filename):
    """Downloads a file from a URL to a local path with a progress bar."""
    if os.path.exists(local_filename):
        print(f"File already exists: {local_filename}")
        return
        
    print(f"Downloading {local_filename} from {url}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size_in_bytes = int(r.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=block_size):
                progress_bar.update(len(chunk))
                f.write(chunk)
        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            print("ERROR, something went wrong during download")

def extract_tarfile(tar_path, extract_path, expected_dir_name):
    """Extracts a .tar.gz file and checks if the content already exists."""
    # Construct the full path to the expected directory
    full_expected_dir = os.path.join(extract_path, expected_dir_name)

    if os.path.exists(full_expected_dir):
        print(f"Dataset directory '{full_expected_dir}' already exists. Skipping extraction.")
        return

    print(f"Extracting {tar_path} to {extract_path}...")
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_path)
        print("Extraction complete.")
    except tarfile.ReadError as e:
        print(f"Error extracting {tar_path}: {e}")
        print("The file might be corrupted or not a valid tar.gz file.")
    except Exception as e:
        print(f"An unexpected error occurred during extraction: {e}")


def main():
    """Main function to download and extract the TUM datasets."""
    datasets_to_download = [
        {
            "url": "https://vision.in.tum.de/rgbd/dataset/freiburg1/rgbd_dataset_freiburg1_xyz.tgz",
            "dir_name": "rgbd_dataset_freiburg1_xyz"
        },
        {
            "url": "https://vision.in.tum.de/rgbd/dataset/freiburg2/rgbd_dataset_freiburg2_desk_with_person.tgz",
            "dir_name": "rgbd_dataset_freiburg2_desk_with_person"
        }
    ]
    
    dataset_dir = "datasets"
    os.makedirs(dataset_dir, exist_ok=True)

    for dataset in datasets_to_download:
        dataset_url = dataset["url"]
        expected_dir_name = dataset["dir_name"]
        # Infer tar filename from URL
        tar_filename = os.path.join(dataset_dir, os.path.basename(dataset_url))

        print(f"\nProcessing dataset: {expected_dir_name}")
        
        # Download the dataset
        download_file(dataset_url, tar_filename)

        # Extract the dataset
        extract_tarfile(tar_filename, dataset_dir, expected_dir_name)

if __name__ == "__main__":
    main()