import numpy as np
import os

def add_noise_to_trajectory(input_file, output_file, noise_std_dev):
    """
    Reads a trajectory file, adds Gaussian noise to the positional data,
    and writes the noisy trajectory to a new file.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return

    trajectory = np.loadtxt(input_file)
    
    # Add noise only to the translation columns (tx, ty, tz)
    positional_data = trajectory[:, 1:4]
    noise = np.random.normal(0, noise_std_dev, positional_data.shape)
    noisy_positional_data = positional_data + noise
    
    # Replace original positions with noisy ones
    noisy_trajectory = trajectory.copy()
    noisy_trajectory[:, 1:4] = noisy_positional_data
    
    # Save the new trajectory
    np.savetxt(output_file, noisy_trajectory, fmt='%f')
    print(f"Generated noisy trajectory: {output_file}")

def main():
    """
    Generates simulated 'estimated' trajectory files with different noise levels
    for specified datasets to represent different SLAM system baselines.
    """
    datasets = [
        "rgbd_dataset_freiburg1_xyz",
        "rgbd_dataset_freiburg2_desk_with_person"
    ]
    
    baselines = [
        {"name": "orbslam3", "noise": 0.02},  # Moderate noise
        {"name": "kimera", "noise": 0.005}   # Low noise
    ]

    base_dir = "datasets"

    for dataset_name in datasets:
        dataset_path = os.path.join(base_dir, dataset_name)
        groundtruth_file = os.path.join(dataset_path, "groundtruth.txt")

        if not os.path.exists(groundtruth_file):
            print(f"Skipping {dataset_name}: groundtruth.txt not found.")
            continue

        print(f"\nProcessing dataset: {dataset_name}")
        
        for baseline in baselines:
            output_filename = f"estimated_{baseline['name']}.txt"
            output_file = os.path.join(dataset_path, output_filename)
            add_noise_to_trajectory(groundtruth_file, output_file, baseline['noise'])

if __name__ == "__main__":
    main()