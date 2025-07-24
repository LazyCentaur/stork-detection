from ultralytics import YOLO
import cv2

# --- TRAINED MODEL ---
model_path = 'runs/detect/stork_experiment_15/weights/best.pt'
model = YOLO(model_path)

# source = 'https://www.youtube.com/watch?v=i_jiHI3k8ag'
source = 'dataset/images/val/sample_frame_044.jpg' 

# --- DO PREDICTION ---
results = model.predict(source=source, save=True, conf=0.5)

print("\nPrediction completed!")
# The results are automatically saved in the 'runs/detect/predict' folder'