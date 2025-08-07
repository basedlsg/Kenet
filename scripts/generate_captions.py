import os
import json
import sys
from PIL import Image
from google import genai
from google.genai import types
from tqdm import tqdm
import gcsfs
from google.cloud import storage

def generate_captions(dataset_dir):
    """
    Generates and verifies captions for all images in the dataset's rgb directory
    using Gemini Pro Vision and saves them to a file.
    """
    # --- API Key Configuration ---
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        try:
            from google.colab import userdata
            api_key = userdata.get('GEMINI_API_KEY')
        except (ImportError, KeyError):
            pass

    if not api_key:
        raise ValueError("Gemini API key not found. Please set the GEMINI_API_KEY environment variable or add it to a .env file.")

    client = genai.Client(api_key=api_key)

    # --- Model Setup ---
    caption_model = "gemini-1.5-pro-latest"
    verifier_model = "gemini-1.5-flash-latest" # Using a text-only model for verification

    # --- Dataset and Output Paths ---
    fs = None
    if dataset_dir.startswith("gs://"):
        fs = gcsfs.GCSFileSystem()
        image_dir = f"{dataset_dir}/rgb"
        output_file = f"{dataset_dir}/captions.txt"
        image_files = sorted([os.path.basename(f) for f in fs.glob(f"{image_dir}/*.png") + fs.glob(f"{image_dir}/*.jpg") + fs.glob(f"{image_dir}/*.jpeg")])
    else:
        image_dir = os.path.join(dataset_dir, "rgb")
        output_file = os.path.join(dataset_dir, "captions.txt")
        if not os.path.exists(image_dir):
            print(f"Error: Image directory not found at {image_dir}")
            return
        image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])

    # --- Caption Generation and Verification ---
    output_stream = fs.open(output_file, "w", encoding="utf-8") if fs else open(output_file, "w", encoding="utf-8")
    with output_stream as f, tqdm(total=len(image_files), desc="Generating and Verifying Captions") as pbar:
        for image_file in image_files:
            image_path = f"{image_dir}/{image_file}"
            try:
                if fs:
                    with fs.open(image_path, 'rb') as img_f:
                        image = Image.open(img_f)
                        image.load()
                else:
                    image = Image.open(image_path)
            except OSError as e:
                print(f"Warning: Could not open or process image file {image_path}. Error: {e}. Skipping.")
                pbar.update(1)
                continue

            # 1. Generate 3 candidate captions
            prompt = "Generate 3 distinct, descriptive captions for this image. Output as a raw JSON list of strings."
            try:
                response = client.models.generate_content(
                    model=caption_model,
                    contents=[image, prompt],
                    config=types.GenerateContentConfig(
                        # No specific config needed for this model for top-k=3
                    )
                )
                response_text = response.text
                if response_text.startswith("```json"):
                    response_text = response_text[7:-4]
                candidate_captions = json.loads(response_text)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Error decoding JSON for {image_file}. Error: {e}. Skipping.")
                pbar.update(1)
                continue

            # 2. Implement a Hallucination Filter
            verified_captions = []
            for caption in candidate_captions:
                verification_prompt = f"""
                As a fact-checker, is the following caption a factually accurate description of the image?
                Caption: "{caption}"
                Respond with only "YES" or "NO".
                """
                try:
                    verification_response = client.models.generate_content(
                        model=verifier_model,
                        contents=[image, verification_prompt]
                    )
                    if "yes" in verification_response.text.lower():
                        verified_captions.append(caption.strip())
                except Exception as e:
                    print(f"Error verifying caption for {image_file}: {e}")


            # 3. Update Output Format
            if verified_captions:
                f.write(f"{image_file}\t" + "\t".join(verified_captions) + "\n")

            pbar.update(1)

    print(f"\nVerified captions saved to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_captions.py <path_to_dataset_directory>")
        sys.exit(1)
    dataset_directory = sys.argv[1]
    generate_captions(dataset_directory)