from ultralytics import YOLO

# Load a model
model = YOLO("yolo11n.pt")

# Train the model
train_results = model.train(
    data="./Schematics_model.yaml",  # path to dataset YAML
    epochs=100,  # number of training epochs
    imgsz=224,  # training image size
    device="0",  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
    batch = 16
)

# Evaluate model performance on the validation set
# metrics = model.val()

# Perform object detection on an image
# results = model("path/to/image.jpg")
# results[0].show()

# Export the model to ONNX format
# path = model.export(format="onnx")  # return path to exported model