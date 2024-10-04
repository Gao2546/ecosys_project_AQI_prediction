import torch
import torchvision.transforms as transforms
from torchvision.ops import nms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import time
import os

# Define image transformations (resize, convert to tensor, normalize)
size = 640
transform = transforms.Compose([
    transforms.Resize((size, size)),  # Resize image to match the model input size
    transforms.ToTensor(),  # Convert image to PyTorch tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize for pre-trained models
])

# Custom Dataset class to load images without labels
class ImageDataset(Dataset):
    def __init__(self, image_folder, transform=None):
        self.image_folder = image_folder
        self.transform = transform
        self.image_paths = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(('.png', '.jpg', '.jpeg'))]
        self.number_of_images = len(self.image_paths)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert("RGB")  # Open and convert image to RGB
        if self.transform:
            image = self.transform(image)
        return image

def nms_function(output):
    output_T = output.permute(1, 0)
    
    boxes = output_T[:, :4]  # Extract bounding boxes (x1, y1, x2, y2)
    # print(boxes.size())
    scores = torch.max(output_T[:, 4:], dim=1)[0]  # Extract class confidence scores and labels

    threshold_score = 0.5

    mask_score = scores >= threshold_score

    scores = scores[mask_score]

    boxes = boxes[mask_score]
        
    # Apply NMS
    iou_threshold = 0.5  # Intersection over Union threshold for NMS
    keep_indices = nms(boxes, scores, iou_threshold,)  # Get indices of boxes to keep
    # print(keep_indices.size())
    
    # Filter boxes and scores
    filtered_boxes = boxes[keep_indices]
    filtered_scores = scores[keep_indices]
    
    return [filtered_boxes, filtered_scores]

# Load your model
model_data = torch.load("./best.pt")
model = model_data['model'].to(device="cpu", dtype=torch.float32)
test_input = torch.rand([1,3,size,size]).to(device="cpu",dtype=torch.float32)
output = model(test_input)


def prediction(path):

    # Load images from the folder without labels
    image_folder = path  # Replace with the path to your image folder
    dataset = ImageDataset(image_folder, transform=transform)

    # Create a DataLoader to load batches of images
    batch_size = 16  # You can adjust batch size as needed
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    images_score = []
    images_bbox = []
    # Time the inference
    with torch.no_grad():
        st = time.time()
        for inputs in data_loader:  # Iterate over the images in the folder
            # st = time.time()
            inputs = inputs.to(device="cpu", dtype=torch.float32)  # Move the input to the device (GPU)
            output = model(inputs)
            for out in output[0].to(device="cpu"):
                filtered_boxes, filtered_scores = nms_function(output=out.to(device = "cpu"))
                images_bbox.append(filtered_boxes)
                images_score.append(filtered_scores)

        stt = time.time()

    print(f"fps = {dataset.number_of_images / (stt - st)}")
    print("Total time: ", stt - st)

    # Apply NMS to the last output
    # st_nms = time.time()
    # for out in output[0].to(device=0):
    #     filtered_boxes, filtered_scores = nms_function(output=out)
    # stt_nms = time.time()

    # print(f"nms_time = {stt_nms - st_nms}")
    # print(f"all_time_fps = {len(dataset) / ((stt - st) + (stt_nms - st_nms))} fps")

    # Output filtered boxes and scores
    print(filtered_boxes)
    print(filtered_scores)
    print(len(filtered_scores))

    # Output shape info
    print(output[0].size())
    print(output[1][0].size())
    print(output[1][1].size())
    print(output[1][2].size())

