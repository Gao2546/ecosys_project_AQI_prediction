import torch
import torchvision.transforms as transforms
from torchvision.ops import nms
from torch.utils.data import Dataset, DataLoader
from PIL import Image , ImageDraw , ImageFont
import time
import os
import random
import pickle

# Define image transformations (resize, convert to tensor, normalize)
font_size = 20
# font = ImageFont.truetype("arial.ttf", font_size)  # Use a .ttf font file, adjust size as needed
font = ImageFont.load_default(font_size)
size = 640
transform = transforms.Compose([
    transforms.Resize((size, size)),  # Resize image to match the model input size
    transforms.ToTensor(),  # Convert image to PyTorch tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize for pre-trained models
])
class_names = ['__background__', 'text', 'junction', 'crossover', 'terminal', 'gnd', 'vss', 'voltage.dc', 'voltage.ac', 'voltage.battery', 
               'resistor', 'resistor.adjustable', 'resistor.photo', 'capacitor.unpolarized', 'capacitor.polarized', 'capacitor.adjustable', 
               'inductor', 'inductor.ferrite', 'inductor.coupled', 'transformer', 'diode', 'diode.light_emitting', 'diode.thyrector', 
               'diode.zener', 'diac', 'triac', 'thyristor', 'varistor', 'transistor.bjt', 'transistor.fet', 'transistor.photo', 
               'operational_amplifier', 'operational_amplifier.schmitt_trigger', 'optocoupler', 'integrated_circuit', 'integrated_circuit.ne555', 
               'integrated_circuit.voltage_regulator', 'xor', 'and', 'or', 'not', 'nand', 'nor', 'probe', 'probe.current', 'probe.voltage', 
               'switch', 'relay', 'socket', 'fuse', 'speaker', 'motor', 'lamp', 'microphone', 'antenna', 'crystal', 'mechanical', 'magnetic', 
               'optical', 'block', 'explanatory', 'unknown']

# Custom Dataset class to load images without labels
class ImageDataset(Dataset):
    def __init__(self, image_folder, transform=None):
        self.image_folder = image_folder
        self.transform = transform
        self.image_paths = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(('.png', '.jpg', '.jpeg'))]
        self.number_of_images = len(self.image_paths)
        # self.size_of_images = []

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert("RGB")  # Open and convert image to RGB
        # self.size_of_images.append(image.size())
        if self.transform:
            image = self.transform(image)
        return image
    
def count_classes(predicted_classes, class_names):
    # Initialize a dictionary to store the count of each class
    class_count = {class_name: 0 for class_name in class_names}
    
    # Count occurrences of each predicted class
    for class_idx in predicted_classes:
        class_name = class_names[class_idx]  # Map class index to class name
        class_count[class_name] += 1  # Increment count
    
    return class_count


def nms_function(output):
    output_T = output.permute(1, 0)
    
    boxes_xywh = output_T[:, :4]  # Extract bounding boxes (x, y, w, h)
    # print(boxes_xywh)
    boxes_xyxy = convert_cxcywh_to_xyxy(boxes_xywh)  # Convert to (x1, y1, x2, y2)
    # print(boxes_xyxy)
    scores = torch.max(output_T[:, 4:], dim=1)[0]  # Extract class confidence scores
    class_obj = torch.argmax(output_T[: , 4:] ,dim=1)
    print(class_obj)

    threshold_score = 0.5
    mask_score = scores >= threshold_score
    class_obj = class_obj[mask_score]
    scores = scores[mask_score]
    boxes_xyxy = boxes_xyxy[mask_score]

    # Apply NMS
    iou_threshold = 0.5  # Intersection over Union threshold for NMS
    keep_indices = nms(boxes_xyxy, scores, iou_threshold)  # Get indices of boxes to keep
    
    # Filter boxes and scores based on NMS results
    filtered_boxes = boxes_xyxy[keep_indices]
    filtered_scores = scores[keep_indices]
    filtered_class = class_obj[keep_indices]
    
    return [filtered_boxes, filtered_scores, filtered_class]

def map_boxes_to_original_size(boxes, original_size, resized_size):
    orig_w, orig_h = original_size
    resized_w, resized_h = resized_size
    
    # Calculate scale factors for width and height
    scale_w = orig_w / resized_w
    scale_h = orig_h / resized_h

    # Scale bounding box coordinates
    mapped_boxes = []
    for box in boxes:
        x1, y1, x2, y2 = box
        x1 = int(x1 * scale_w)
        y1 = int(y1 * scale_h)
        x2 = int(x2 * scale_w)
        y2 = int(y2 * scale_h)
        mapped_boxes.append([x1, y1, x2, y2])
    
    return mapped_boxes

def convert_cxcywh_to_xyxy(boxes):
    """
    Convert boxes from [center_x, center_y, width, height] format 
    to [x1, y1, x2, y2] (top-left corner, bottom-right corner).
    """
    new_boxes = torch.zeros_like(boxes)
    new_boxes[:, 0] = boxes[:, 0] - (boxes[:, 2] / 2)  # x1 = center_x - width / 2
    new_boxes[:, 1] = boxes[:, 1] - (boxes[:, 3] / 2)  # y1 = center_y - height / 2
    new_boxes[:, 2] = boxes[:, 0] + (boxes[:, 2] / 2)  # x2 = center_x + width / 2
    new_boxes[:, 3] = boxes[:, 1] + (boxes[:, 3] / 2)  # y2 = center_y + height / 2
    return new_boxes


def draw_boxes(image, boxes, scores,classO):
    draw = ImageDraw.Draw(image)
    for i, box in enumerate(boxes):
        color = random_rgb_color()
        x1, y1, x2, y2 = box
        score = scores[i].item()
        # print(score)
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)  # Draw bounding box
        draw.text((x2+3, y1), f"{score:.2f} {classO[i]}", fill=color,stroke_width=1,font=font,spacing=20)  # Add score as text above the box
        # draw.text((x1,y1), "test" , fill='green')
    # print("end_draw_image")
    return image

# Load your model
model_data = torch.load("./best.pt")
model = model_data['model'].to(device="cpu", dtype=torch.float32)
test_input = torch.rand([1,3,size,size]).to(device="cpu",dtype=torch.float32)
output = model(test_input)

def random_rgb_color():
    r = random.randint(0, 255)  # Red channel (8-bit)
    g = random.randint(0, 255)  # Green channel (8-bit)
    b = random.randint(0, 255)  # Blue channel (8-bit)
    return (r, g, b)

def prediction(path, output_folder,username):
    # Load images from the folder without labels
    image_folder = path  # Replace with the path to your image folder
    dataset = ImageDataset(image_folder, transform=transform)

    # Create a DataLoader to load batches of images
    batch_size = 16  # You can adjust batch size as needed
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    images_score = []
    images_bbox = []
    images_class = []
    images_path = []
    
    # Time the inference
    with torch.no_grad():
        st = time.time()
        total_class_counts = {class_name: 0 for class_name in class_names}
        for batch_idx, inputs in enumerate(data_loader):  # Iterate over the images in the folder
            inputs = inputs.to(device="cpu", dtype=torch.float32)  # Move the input to the device (GPU)
            output = model(inputs)

            for i, out in enumerate(output[0].to(device="cpu")):
                filtered_boxes, filtered_scores, filtered_class = nms_function(output=out.to(device="cpu"))
                images_bbox.append(filtered_boxes)
                images_score.append(filtered_scores)
                # images_class.append(filtered_class)

                batch_class_counts = count_classes(filtered_class, class_names)
                
                # Update total class counts
                for class_name, count in batch_class_counts.items():
                    total_class_counts[class_name] += count
                
                print(f"class = {total_class_counts}")
                images_class.append(total_class_counts)

                # Load the original image before transformation
                original_image_path = dataset.image_paths[batch_idx * batch_size + i]
                original_image = Image.open(original_image_path).convert("RGB")
                original_size = original_image.size  # Get the original size (width, height)
                # original_size = dataset.size_of_images[(batch_idx*batch_size) + i]
                
                images_path.append(dataset.image_paths[batch_idx * batch_size + i])

                # Map the bounding boxes back to the original image size
                resized_size = (size, size)  # The size after resizing (defined earlier in the transform)
                mapped_boxes = map_boxes_to_original_size(filtered_boxes, original_size, resized_size)

                # Draw boxes on the original image using the mapped coordinates
                image_with_boxes = draw_boxes(original_image, mapped_boxes, filtered_scores,filtered_class)
                
                # Save the image with bounding boxes
                output_image_path = os.path.join(output_folder, f"image_{batch_idx * batch_size + i}_bbox.jpg")
                image_with_boxes.save(output_image_path)

        stt = time.time()

    dummp_file = [username,output_folder,images_path,images_class]

    with open(os.path.join(output_folder,"list_data"),"wb") as f:
        pickle.dump(dummp_file,f)


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