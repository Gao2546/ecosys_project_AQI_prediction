import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch.optim as optim

last_train = 100

# Define transformations (e.g., resizing, normalization)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# Load datasets
train_dataset = datasets.ImageFolder(root='/home/athip/psu/3/ecosys/proj/dev/model/data/airpollution/Air Pollution Image Dataset/Air Pollution Image Dataset/Combined_Dataset/IND_and_NEP', transform=transform)
# valid_dataset = datasets.ImageFolder(root='dataset/valid', transform=transform)

# Create DataLoaders
train_loader = DataLoader(dataset=train_dataset, batch_size=16, shuffle=True)
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

AQI_model_base.load_state_dict(torch.load('/home/athip/psu/3/ecosys/proj/dev/model/checkpoint/AQI_model_base99.pt'))

# criterion = nn.CrossEntropyLoss()
# optimizer = optim.Adam(AQI_model_base.parameters(), lr=0.001)

# Training loop
num_epochs = 1
for epoch in range(num_epochs):
    AQI_model_base.eval()  # Set the model to training mode
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)

        # Zero the gradients
        # optimizer.zero_grad()

        # Forward pass
        outputs = AQI_model_base(images)
        print(outputs)
        print(torch.argmax(outputs,dim=1))
        print(labels)
        break
        # loss = criterion(outputs, labels)

        # Backward pass and optimization
        # loss.backward()
        # optimizer.step()

        # running_loss += loss.item()

    # Print epoch loss
    # print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}')
    # if (epoch + 1) % 10 == 0 :
    #     torch.save(AQI_model_base.state_dict(), f'/home/athip/psu/3/ecosys/proj/dev/model/checkpoint/AQI_model_base{epoch + last_train}.pt')

# print('Training complete!')