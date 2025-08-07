import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision.models import mobilenet_v2
from PIL import Image
import torchvision.transforms as transforms
import numpy as np

# --- Dataset Definition ---
class SiameseDataset(Dataset):
    def __init__(self, image_pairs, labels, transform=None):
        self.image_pairs = image_pairs
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_pairs)

    def __getitem__(self, idx):
        img1_path, img2_path = self.image_pairs[idx]
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')
        label = self.labels[idx]

        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)

        return img1, img2, torch.from_numpy(np.array([label], dtype=np.float32))

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

# --- Training Loop ---
def train(model, dataloader, criterion, optimizer, num_epochs=10):
    for epoch in range(num_epochs):
        for i, (img1, img2, label) in enumerate(dataloader):
            optimizer.zero_grad()
            output = model(img1, img2)
            loss = criterion(output, label)
            loss.backward()
            optimizer.step()

            if (i+1) % 1 == 0:
                print(f"Epoch [{epoch+1}/{num_epochs}], Step [{i+1}/{len(dataloader)}], Loss: {loss.item():.4f}")

# --- Main ---
if __name__ == "__main__":
    # Define the image transformations
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Create a dummy dataset
    image_pairs = [("prototypes/image1.jpg", "prototypes/image2.jpg"), ("prototypes/image1.jpg", "prototypes/image3.jpg")]
    labels = [1.0, 0.0]  # 1.0 = similar, 0.0 = different
    dataset = SiameseDataset(image_pairs, labels, transform=transform)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

    # Create the model, criterion, and optimizer
    model = SiameseMobileNet()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Train the model
    train(model, dataloader, criterion, optimizer)