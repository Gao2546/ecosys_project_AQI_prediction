import pickle
with open("/home/athip/psu/3/ecosys/proj/dev/model/list_data","rb") as f:
    list_output = pickle.load(f)
username,output_image_path,images_path,images_class = list_output
print(images_class[1])
