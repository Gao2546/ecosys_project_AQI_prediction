import os

# Specify the folder path
folder_path = "/home/athip/psu/3/ecosys/proj/dev/model/data/airpollution (1)/Air Pollution Image Dataset/Air Pollution Image Dataset/Combined_Dataset/IND_and_NEP/f_Severe"

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    # Check if the file name contains spaces
    if ' ' in filename:
        # Create the new filename by replacing spaces with underscores (or remove them)
        new_filename = filename.replace(' ', '')  # Use ''.join(filename.split()) to remove spaces instead

        # Get the full file paths
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(old_file_path, new_file_path)
        print(f"Renamed: '{filename}' -> '{new_filename}'")
