import cv2
import time
from ultralytics import YOLO
import yt_dlp
import os

# --- CONFIGURATION ---
MODEL_PATH = 'runs/detect/stork_experiment_15/weights/best.pt'
YOUTUBE_URL = 'https://www.youtube.com/watch?v=i_jiHI3k8ag'
CONFIDENCE_THRESHOLD = 0.5
LOOP_INTERVAL_SECONDS = 600 # 10 minutos
OUTPUT_DIR = 'runs/detect/realtime'

print("Loading the stork detection model...")
model = YOLO(MODEL_PATH)
os.makedirs(OUTPUT_DIR, exist_ok=True)
print("Model loaded. Starting real-time detection loop.")
print(f"A detection will be run every {int(LOOP_INTERVAL_SECONDS / 60)} minutes.")
print("Press Ctrl+C to stop the script.")

try:
    while True:
        print(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        print("Getting the YouTube stream URL...")
        
        try:
            # Get the stream URL to ensure it's the most recent
            ydl_opts = {'format': 'best', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(YOUTUBE_URL, download=False)
                stream_url = info_dict.get('url', None)

            if not stream_url:
                print("Get the stream URL to ensure it's the most recent.")
                time.sleep(LOOP_INTERVAL_SECONDS)
                continue

            # --- MANUAL FRAME CAPTURE ---
            print("Abriendo stream con OpenCV para capturar un fotograma...")
            cap = cv2.VideoCapture(stream_url)
            time.sleep(2) # Short pause to allow the stream to stabilize
            success, frame = cap.read()
            cap.release() # We close the connection immediately

            if success:
                # --- PREDICTION ON THE CAPTURED FRAME ---
                print("Captured frame. Making prediction...")
                results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, save=False)
                
                # We save the image with the detections
                annotated_frame = results[0].plot()
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                output_path = os.path.join(OUTPUT_DIR, f'detection_{timestamp}.jpg')
                cv2.imwrite(output_path, annotated_frame)
                print(f"Detection completed! Image saved in: {output_path}")
            else:
                print("Could not capture a frame from the stream on this attempt.")

        except Exception as e:
            print(f"An error occurred: {e}")
        
        # --- WAIT ---
        print(f"Waiting {int(LOOP_INTERVAL_SECONDS / 60)} minutes to the next cycle...")
        time.sleep(LOOP_INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("\nScript stopped by user. Goodbye!")