from ultralytics import YOLO
import cv2

model_path = 'runs/detect/stork_experiment_n2/weights/best.pt'
model = YOLO(model_path)

source = 'dataset/images/val/sample_frame_044.jpg' 

results = model.predict(source=source, save=True, conf=0.5)

print("\nPrediction completed!")