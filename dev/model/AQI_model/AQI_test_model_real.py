import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch.optim as optim

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class UnlabeledImageDataset(Dataset):
    def __init__(self, folder_path, transform=None):
        self.folder_path = folder_path
        self.transform = transform
        self.image_files = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_path = os.path.join(self.folder_path, self.image_files[idx])
        image = Image.open(img_path).convert("RGB")  # Convert to RGB if needed

        if self.transform:
            image = self.transform(image)

        return image

# Specify the folder containing images
folder_path = '/home/athip/psu/3/ecosys/proj/dev/model/data/test_real_image'

# Define transformations if needed
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize images
    transforms.ToTensor(),           # Convert images to tensors
])

# Create dataset and dataloader
dataset = UnlabeledImageDataset(folder_path, transform=transform)
data_loader = DataLoader(dataset, batch_size=16, shuffle=True)

class Model(nn.Module):
    def __init__(self,mobile_net,fcc_layer):
        super().__init__()
        self.mobile_netv2 = mobile_net
        self.avgpooling = nn.AdaptiveAvgPool2d(1)
        self.fcc = fcc_layer
        self.flatten = nn.Flatten()

    def forward(self, x):
        output = self.fcc(self.flatten(self.avgpooling(self.mobile_netv2(x))))
        return output
    
model = torch.hub.load('pytorch/vision:v0.10.0', 'mobilenet_v2', pretrained=True)

AQI_model_base = Model(list(model.children())[0],list(model.children())[1]).to(device=device)

AQI_model_base.load_state_dict(torch.load('/home/athip/psu/3/ecosys/proj/dev/model/checkpoint/AQI_model_base_hatyai_10.pt'))

# Example of iterating over the DataLoader
AQI_model_base.eval()
for images in data_loader:
    outputs = AQI_model_base(images.to(device = device))
    print(outputs)
    print(torch.argmax(outputs,dim=1))
    print([0,0,0,0,1,1])
    print(images.shape)  # Each batch of images
