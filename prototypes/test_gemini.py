import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import numpy as np

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

def main():
    """
    Tests the Gemini embedding and similarity calculation.
    """
    img1_path = "prototypes/image1.jpg"
    img2_path = "prototypes/image2.jpg"

    print("Generating captions...")
    caption1 = generate_caption(img1_path)
    caption2 = generate_caption(img2_path)
    print("Captions generated.")

    print("Generating embeddings...")
    response = genai.embed_content(
        model="models/embedding-001",
        content=[caption1, caption2],
        task_type="RETRIEVAL_DOCUMENT"
    )
    print("Embeddings generated.")

    embeddings = response['embedding']
    
    # Correctly unpack the embeddings
    embedding1 = np.array(embeddings)
    embedding2 = np.array(embeddings)

    # Calculate cosine similarity
    similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    print("\n--- Gemini Test Results ---")
    print(f"Caption 1: {caption1}")
    print(f"Caption 2: {caption2}")
    print(f"Embedding 1 shape: {embedding1.shape}")
    print(f"Embedding 2 shape: {embedding2.shape}")
    print(f"Similarity: {similarity:.4f}")

if __name__ == "__main__":
    main()