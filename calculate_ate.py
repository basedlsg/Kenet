import sys
import numpy as np
from evo.core import trajectory, sync
from evo.tools import file_interface
from evo.core import metrics

def calculate_ate(file_gt: str, file_est: str):
    """
    Calculates the Absolute Trajectory Error (ATE) between a ground truth
    and an estimated trajectory.
    """
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

    print("\n--- Absolute Trajectory Error (ATE) ---")
    print(f"  Max:    {ate_stats['max']:.4f}")
    print(f"  Mean:   {ate_stats['mean']:.4f}")
    print(f"  Median: {ate_stats['median']:.4f}")
    print(f"  Min:    {ate_stats['min']:.4f}")
    print(f"  RMSE:   {ate_stats['rmse']:.4f}")
    print(f"  SSE:    {ate_stats['sse']:.4f}")
    print(f"  Std:    {ate_stats['std']:.4f}")
    print("------------------------------------")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python calculate_ate.py <ground_truth.txt> <estimated.txt>")
        sys.exit(1)
    
    calculate_ate(sys.argv[1], sys.argv[2])