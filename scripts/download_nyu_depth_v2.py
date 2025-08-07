import argparse
import io
import pandas as pd
from PIL import Image
from tqdm import tqdm
import gcsfs
from huggingface_hub import hf_hub_download, list_repo_files

def download_and_process_nyu_depth_v2(output_path):
    """
    Downloads the NYU Depth Dataset V2 from Hugging Face by fetching all
    partial Parquet files, concatenating them, and saving the RGB images
    from the 'train' split to a Google Cloud Storage bucket.

    Args:
        output_path (str): The GCS path to the output directory (e.g., gs://bucket/path).
    """
    # Ensure necessary packages are installed:
    # pip install gcsfs google-cloud-storage pandas pyarrow huggingface-hub tqdm Pillow
    # Ensure you are authenticated with GCP:
    # gcloud auth application-default login
    
    fs = gcsfs.GCSFileSystem()

    # Create the output directory if it doesn't exist
    rgb_output_path = f"{output_path}/rgb"
    if not fs.exists(rgb_output_path):
        fs.mkdirs(rgb_output_path, exist_ok=True)

    # Get the list of all partial training files
    repo_id = "sayakpaul/nyu_depth_v2"
    revision = "refs/convert/parquet"
    print(f"Listing partial training files from '{repo_id}'...")
    try:
        all_files = list_repo_files(repo_id=repo_id, repo_type="dataset", revision=revision)
        train_files = [f for f in all_files if f.startswith("default/partial-train/")]
        if not train_files:
            print("Error: No partial training files found.")
            return
        print(f"Found {len(train_files)} partial training files.")
    except Exception as e:
        print(f"Failed to list repository files: {e}")
        return

    # Download and concatenate all partial parquet files
    all_dataframes = []
    print("Downloading and processing partial files...")
    for filename in tqdm(train_files, desc="Downloading Parquet parts"):
        try:
            parquet_file_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                repo_type="dataset",
                revision=revision
            )
            df_part = pd.read_parquet(parquet_file_path)
            all_dataframes.append(df_part)
        except Exception as e:
            print(f"\nFailed to download or process {filename}: {e}")
            continue
    
    if not all_dataframes:
        print("No data was downloaded. Exiting.")
        return

    # Combine all dataframes
    df = pd.concat(all_dataframes, ignore_index=True)
    print(f"\nDataset loaded successfully. Total samples: {df.shape[0]}")

    # Iterate through the dataset and save the RGB images
    print(f"Saving RGB images to {rgb_output_path}...")
    for i, row in tqdm(df.iterrows(), total=df.shape[0], desc="Saving images"):
        image_bytes = row['image']['bytes']
        image = Image.open(io.BytesIO(image_bytes))
        image_path = f"{rgb_output_path}/{i:06d}.png"
        with fs.open(image_path, 'wb') as f:
            image.save(f, format='PNG')

    print("All RGB images have been saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and process the NYU Depth Dataset V2 and save to GCS.")
    parser.add_argument("output_path", type=str, help="The GCS path to the output directory (e.g., gs://bucket-name/folder).")
    args = parser.parse_args()

    download_and_process_nyu_depth_v2(args.output_path)