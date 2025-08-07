import torch
import torch.nn as nn
from torchvision.models import mobilenet_v2
from PIL import Image
import torchvision.transforms as transforms

# --- Model Definition ---
class SiameseMobileNet(nn.Module):
    def __init__(self):
        super(SiameseMobileNet, self).__init__()
        self.mobilenet = mobilenet_v2(pretrained=True)
        self.fc = nn.Sequential(
            nn.Linear(1000, 256),
            nn.ReLU(inplace=True),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward_one(self, x):
        x = self.mobilenet(x)
        return x

    def forward(self, x1, x2):
        out1 = self.forward_one(x1)
        out2 = self.forward_one(x2)
        diff = torch.abs(out1 - out2)
        out = self.fc(diff)
        return out

# --- Image Loading and Preprocessing ---
def load_image(image_path):
    """Loads and preprocesses an image."""
    image = Image.open(image_path).convert('RGB')
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return preprocess(image).unsqueeze(0)

# --- Main ---
if __name__ == "__main__":
    # Load the model
    model = SiameseMobileNet()
    model.eval()

    # Load two images
    img1 = load_image("image1.jpg")
    img2 = load_image("image2.jpg")

    # Get the similarity score
    similarity = model(img1, img2)
    print(f"Similarity score: {similarity.item():.4f}")