from google.cloud import aiplatform

def run_training_job(project_id: str, location: str, staging_bucket: str):
    """Runs a Vertex AI training job."""
    aiplatform.init(project=project_id, location=location, staging_bucket=staging_bucket)
    job = aiplatform.CustomTrainingJob(
        display_name="pruning-model-training",
        script_path="scripts/train_pruning_model.py",
        container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-12:latest",
        requirements=["google-cloud-storage"],
        model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/pytorch-gpu.1-12:latest",
    )
    job.run()

if __name__ == "__main__":
    run_training_job(
        project_id="vertex-test-1-467818",
        location="us-central1",
        staging_bucket="gs://atropos_bucket",
    )