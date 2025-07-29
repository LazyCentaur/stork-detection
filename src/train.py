from ultralytics import YOLO

model = YOLO('runs/detect/stork_experiment_n2/weights/best.pt')

results = model.train(
   data='data.yaml',
   cache=False,
   epochs=100,
   imgsz=640,
   project='runs/detect',
   name='stork_experiment_n'
)

print("Training completed!")