import os
from PIL import Image

# Specify the folder paths
input_folder = "/home/athip/psu/3/ecosys/proj/dev/model/data/Hatyai/b_Moderate"      # Folder containing original images
output_folder = "/home/athip/psu/3/ecosys/proj/dev/model/data/Hatyai/b_Moderate"    # Folder to save resized images

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

width = 224
height = 224
# Define the new size (width, height)
new_size = (width, height)  # Replace with desired dimensions

# Loop through all files in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        # Open the image
        img_path = os.path.join(input_folder, filename)
        with Image.open(img_path) as img:
            # Resize the image
            resized_img = img.resize(new_size)
            
            # Save the resized image to the output folder
            output_path = os.path.join(output_folder, filename)
            resized_img.save(output_path)

            print(f"Resized and saved: {output_path}")
