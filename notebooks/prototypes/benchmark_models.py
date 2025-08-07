import torch
import time
import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import numpy as np
from train_mobilenet import SiameseMobileNet, SiameseDataset
from torchvision import transforms
from torch.utils.data import DataLoader

# --- Gemini API Key Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found.")
    exit()
genai.configure(api_key=GEMINI_API_KEY)

def generate_caption(image_path):
    """
    Generates a caption for a single image.
    """
    img = Image.open(image_path)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(
        ["Generate a descriptive caption for this image.", img]
    )
    return response.text

def benchmark_mobilenet():
    """
    Benchmarks the MobileNetV2 model.
    """
    # Create a dummy dataset
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    image_pairs = [("prototypes/image1.jpg", "prototypes/image2.jpg"), ("prototypes/image1.jpg", "prototypes/image3.jpg")]
    labels = [1.0, 0.0]
    dataset = SiameseDataset(image_pairs, labels, transform=transform)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

    # Load the model
    model = SiameseMobileNet()
    model.eval()

    # Run the benchmark
    total_time = 0
    correct = 0
    with torch.no_grad():
        for img1, img2, label in dataloader:
            start_time = time.time()
            output = model(img1, img2)
            end_time = time.time()
            total_time += end_time - start_time
            pred = torch.round(output)
            correct += (pred == label).sum().item()

    accuracy = correct / len(dataset)
    avg_latency = total_time / len(dataset)

    print("--- MobileNetV2 Benchmark Results ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Average Latency: {avg_latency:.4f}s")

def benchmark_gemini():
    """
    Benchmarks the gemini-1.5-flash model.
    """
    # Create a dummy dataset
    image_pairs = [("prototypes/image1.jpg", "prototypes/image2.jpg"), ("prototypes/image1.jpg", "prototypes/image3.jpg")]
    labels = [1.0, 0.0]

    # Run the benchmark
    total_time = 0
    correct = 0
    for (img1_path, img2_path), label in zip(image_pairs, labels):
        start_time = time.time()
        
        caption1 = generate_caption(img1_path)
        caption2 = generate_caption(img2_path)
        
        response = genai.embed_content(
            model="models/embedding-001",
            content=[caption1, caption2],
            task_type="RETRIEVAL_DOCUMENT"
        )
        
        embeddings = response['embedding']
        embedding1 = np.array(embeddings[0])  # First embedding
        embedding2 = np.array(embeddings[1])  # Second embedding

        similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        
        end_time = time.time()
        total_time += end_time - start_time
        
        pred = 1.0 if similarity > 0.8 else 0.0
        correct += 1 if pred == label else 0

    accuracy = correct / len(image_pairs)
    avg_latency = total_time / len(image_pairs)

    print("--- Gemini-1.5-Flash Benchmark Results ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Average Latency: {avg_latency:.4f}s")

if __name__ == "__main__":
    benchmark_mobilenet()
    benchmark_gemini()