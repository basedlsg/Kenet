import os
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, GPT2Tokenizer
from tqdm import tqdm

def generate_captions():
    """
    Generates captions for all images in the dataset's rgb directory
    and saves them to a file.
    """
    # --- Model and Tokenizer Setup ---
    model_name = "nlpconnect/vit-gpt2-image-captioning"
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    image_processor = ViTImageProcessor.from_pretrained(model_name)
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    # --- Dataset and Output Paths ---
    image_dir = "datasets/rgbd_dataset_freiburg1_xyz/rgb"
    output_file = "captions.txt"

    if not os.path.exists(image_dir):
        print(f"Error: Image directory not found at {image_dir}")
        return

    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])

    # --- Caption Generation ---
    with open(output_file, "w") as f, tqdm(total=len(image_files), desc="Generating Captions") as pbar:
        for image_file in image_files:
            image_path = os.path.join(image_dir, image_file)
            image = Image.open(image_path).convert("RGB")

            # Process image
            pixel_values = image_processor(images=image, return_tensors="pt").pixel_values
            pixel_values = pixel_values.to(device)

            # Generate caption
            output_ids = model.generate(pixel_values, max_length=16)
            caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)

            f.write(f"{image_file}\t{caption}\n")
            pbar.update(1)

    print(f"\nCaptions saved to {output_file}")

if __name__ == "__main__":
    generate_captions()