from ultralytics import YOLO

# --- Load a pre-trained model ---
# We load 'yolov8s.pt'. 's' stands for 'small' model
model = YOLO('yolov8s.pt')

# --- Train the model with our data ---
results = model.train(
   data='notebooks/data.yaml',         # Our data configuration file.
   epochs=100,                         # Number of times the model will see all the data.
   imgsz=640,                          # Image sizes for training.
   project='runs/detect',              # Directory where the results will be saved.
   name='stork_experiment_15'          # Name of the specific folder for this training.
)

print("Training completed!")
print("You can find the results in the folder 'runs/detect/stork_experiment_'")