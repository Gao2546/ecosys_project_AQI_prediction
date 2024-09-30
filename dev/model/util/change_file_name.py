import os

def rename_images(directory, prefix="TH_Hatyai_Good_1_"):
    # List all files in the specified directory
    files = os.listdir(directory)

    # Filter out only image files (you can add more extensions if needed)
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
    images = [f for f in files if f.lower().endswith(image_extensions)]

    # Loop through each image and rename it
    for index, image in enumerate(images, start=1):
        old_path = os.path.join(directory, image)
        new_filename = f"{prefix}{index}{os.path.splitext(image)[1]}"
        new_path = os.path.join(directory, new_filename)

        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed '{image}' to '{new_filename}'")

# Example usage:
rename_images("/home/athip/psu/3/ecosys/proj/dev/model/data/Hatyai​/a_Good")
