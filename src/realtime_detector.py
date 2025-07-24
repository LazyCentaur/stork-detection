# File: realtime_detector.py
import cv2
import time
from ultralytics import YOLO
import yt_dlp
import os
import csv

# --- CONFIGURATION ---
MODEL_PATH = 'runs/detect/stork_experiment_152/weights/best.pt'
YOUTUBE_URL = 'https://www.youtube.com/watch?v=i_jiHI3k8ag'
CONFIDENCE_THRESHOLD = 0.5
LOOP_INTERVAL_SECONDS = 60 # 1 minute for faster testing
OUTPUT_DIR = 'runs/detect/realtime'
LOG_FILE = 'detections_log.csv' # The CSV file to store our data

# --- INITIALIZATION ---
print("Loading the stork detection model...")
model = YOLO(MODEL_PATH)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Create the log file and write the header if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'stork_count']) # Header row

print("Model loaded. Starting real-time detection loop.")
print(f"A detection will run every {int(LOOP_INTERVAL_SECONDS / 60)} minute(s).")
print("Press Ctrl+C to stop the script.")

# --- MAIN LOOP ---
try:
    while True:
        print(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        print("Getting YouTube stream URL...")

        try:
            # Get the stream URL to ensure it's the latest one
            ydl_opts = {'format': 'best', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(YOUTUBE_URL, download=False)
                stream_url = info_dict.get('url', None)

            if not stream_url:
                print("Could not get stream URL. Retrying in the next cycle.")
                time.sleep(LOOP_INTERVAL_SECONDS)
                continue

            # Capture a single frame manually
            print("Opening stream with OpenCV to capture a frame...")
            cap = cv2.VideoCapture(stream_url)
            time.sleep(2) # Brief pause for the stream to stabilize
            success, frame = cap.read() # The 'success' variable is defined here
            cap.release()

            if success:
                # Run prediction on the captured frame
                print("Frame captured. Running prediction...")
                results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, save=False, verbose=False)

                # --- Data Logging ---
                timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S')
                detection_count = len(results[0].boxes) # Count detected boxes

                with open(LOG_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp_str, detection_count])
                
                print(f"Found {detection_count} storks. Data logged.")

                # --- Image Saving ---
                annotated_frame = results[0].plot()
                output_path = os.path.join(OUTPUT_DIR, f'detection_{time.strftime("%Y%m%d_%H%M%S")}.jpg')
                cv2.imwrite(output_path, annotated_frame)
                print(f"Detection image saved to: {output_path}")
            else:
                print("Could not capture a frame from the stream.")
        
        except Exception as e:
            print(f"An error occurred in the detection cycle: {e}")

        # --- WAIT ---
        print(f"Waiting {int(LOOP_INTERVAL_SECONDS / 60)} minute(s) for the next cycle...")
        time.sleep(LOOP_INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("\nScript stopped by user. Goodbye!")