import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch.optim as optim
import torchvision.transforms.v2 as T
import tqdm

last_train = 110
set_train = "hatyai"

size=224
hsv_h=0.015
hsv_s=0.05
hsv_v=0.04
degrees=[-15.0,15.0]
translate=0.1
scale_d=0.8
scale_u=1.2
shear=0.0
perspective=0.0
flipud=0.0
fliplr=0.5
mosaic=1.0
mixup=0.0
copy_paste=0.0

# Define transformations (e.g., resizing, normalization)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
transform = transforms.Compose([
    # transforms.Resize((224, 224)),
    T.RandomResizedCrop(size=(size,size),scale=(scale_d,scale_u),),
    T.RandomPerspective(distortion_scale=perspective,p=0.5),
    T.RandomHorizontalFlip(p=fliplr),
    # T.RandomVerticalFlip(p=flipud),
    # T.RandomRotation(degrees=degrees),
    T.ColorJitter(brightness=hsv_v,contrast=0,saturation=hsv_s,hue=hsv_h),
    T.RandomAffine(translate=(translate,translate),shear=shear,degrees=degrees),
    transforms.ToTensor()
])

# Load datasets
train_dataset = datasets.ImageFolder(root='/home/athip/psu/3/ecosys/proj/dev/model/data/airpollution/Air Pollution Image Dataset/Air Pollution Image Dataset/Combined_Dataset/IND_and_NEP', transform=transform)
# valid_dataset = datasets.ImageFolder(root='dataset/valid', transform=transform)

# Create DataLoaders
train_loader = DataLoader(dataset=train_dataset, batch_size=16*2, shuffle=True)
# valid_loader = DataLoader(dataset=valid_dataset, batch_size=16, shuffle=False)

# device = torch.cuda.device(0)
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

AQI_model_base = Model(list(model.children())[0],list(model.children())[1]).to(device=0)

AQI_model_base.load_state_dict(torch.load('/home/athip/psu/3/ecosys/proj/dev/model/checkpoint/AQI_model_base_hatyai_100.pt'))

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(AQI_model_base.parameters(), lr=0.001)

# Training loop
num_epochs = 100
for epoch in range(num_epochs):
    AQI_model_base.train()  # Set the model to training mode
    running_loss = 0.0
    for images, labels in tqdm.tqdm(train_loader):
        images, labels = images.to(device), labels.to(device)

        # Zero the gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = AQI_model_base(images)
        loss = criterion(outputs, labels)

        # Backward pass and optimization
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    # Print epoch loss
    print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}')
    if (epoch + 1) % 10 == 0 :
        torch.save(AQI_model_base.state_dict(), f'/home/athip/psu/3/ecosys/proj/dev/model/checkpoint/AQI_model_base_{set_train}_{epoch + last_train + 1}.pt')

print('Training complete!')