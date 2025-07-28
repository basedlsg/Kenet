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

def extract_tarfile(tar_path, extract_path):
    """Extracts a .tar.gz file."""
    if os.path.exists(os.path.join(extract_path, "rgbd_dataset_freiburg1_xyz")):
        print(f"Dataset already extracted in {extract_path}")
        return

    print(f"Extracting {tar_path} to {extract_path}...")
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=extract_path)
    print("Extraction complete.")

def main():
    """Main function to download and extract the TUM dataset."""
    dataset_url = "https://vision.in.tum.de/rgbd/dataset/freiburg1/rgbd_dataset_freiburg1_xyz.tgz"
    dataset_dir = "datasets"
    tar_filename = os.path.join(dataset_dir, "rgbd_dataset_freiburg1_xyz.tgz")

    # Create datasets directory if it doesn't exist
    os.makedirs(dataset_dir, exist_ok=True)

    # Download the dataset
    download_file(dataset_url, tar_filename)

    # Extract the dataset
    extract_tarfile(tar_filename, dataset_dir)

if __name__ == "__main__":
    main()