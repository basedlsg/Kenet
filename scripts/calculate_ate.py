import sys
import numpy as np
from evo.core import trajectory, sync
from evo.tools import file_interface
from evo.core import metrics

import os
import glob
from google.cloud import storage

def calculate_ate(file_gt: str, file_est: str):
    """
    Calculates and prints the Absolute Trajectory Error (ATE) between a
    ground truth and an estimated trajectory.
    """
    try:
        # Load trajectories
        traj_gt = file_interface.read_tum_trajectory_file(file_gt)
        traj_est = file_interface.read_tum_trajectory_file(file_est)

        # Synchronize and align trajectories
        traj_ref, traj_est_aligned = sync.associate_trajectories(traj_gt, traj_est)
        traj_est_aligned.align(traj_ref, correct_scale=False)

        # Calculate ATE
        pose_relation = metrics.PoseRelation.translation_part
        data = (traj_ref, traj_est_aligned)
        ape_metric = metrics.APE(pose_relation)
        ape_metric.process_data(data)
        
        ate_stats = ape_metric.get_all_statistics()

        print(f"\n--- ATE Results for: {os.path.basename(file_est)} ---")
        print(f"  RMSE:   {ate_stats['rmse']:.4f} m")
        print(f"  Mean:   {ate_stats['mean']:.4f} m")
        print(f"  Median: {ate_stats['median']:.4f} m")
        print(f"  Std:    {ate_stats['std']:.4f} m")
        print(f"  Min:    {ate_stats['min']:.4f} m")
        print(f"  Max:    {ate_stats['max']:.4f} m")
        print("-------------------------------------------")

    except FileNotFoundError as e:
        print(f"Error: {e}. Check your file paths.")
    except Exception as e:
        print(f"An unexpected error occurred while processing {file_est}: {e}")


def download_from_gcs(bucket_name, source_blob_name, destination_file_name):
    """Downloads a file from the bucket."""
    storage_client = storage.Client(project="amien-research-pipeline")
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print(
        f"Blob {source_blob_name} downloaded to {destination_file_name}."
    )


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python calculate_ate.py <gcs_bucket> <ground_truth_trajectory> <estimated_trajectory>")
        sys.exit(1)
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/carlos/.config/gcloud/application_default_credentials.json"
    gcs_bucket = sys.argv[1]
    ground_truth_file = sys.argv[2]
    estimated_file = sys.argv[3]

    # Download files from GCS
    download_from_gcs(gcs_bucket, ground_truth_file, os.path.basename(ground_truth_file))
    download_from_gcs(gcs_bucket, estimated_file, os.path.basename(estimated_file))

    calculate_ate(os.path.basename(ground_truth_file), os.path.basename(estimated_file))