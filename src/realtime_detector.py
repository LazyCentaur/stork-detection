# File: realtime_detector.py
import cv2
import time
from ultralytics import YOLO
import yt_dlp
import os
import sqlite3
import atexit

# --- CONFIGURATION ---
MODEL_PATH = 'runs/detect/stork_experiment_n3/weights/best.pt' # Make sure it's the latest model
YOUTUBE_URL = 'https://www.youtube.com/watch?v=5YITOvRxKWU'
CONFIDENCE_THRESHOLD = 0.4
LOOP_INTERVAL_SECONDS = 300 # 5 minutes
OUTPUT_DIR = 'runs/detect/realtime'
DB_FILE = 'storks.db'

# --- DATABASE SETUP ---
db_conn = sqlite3.connect(DB_FILE)
cursor = db_conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        stork_count INTEGER NOT NULL,
        image_path TEXT
    )
''')
db_conn.commit()

def close_db():
    if db_conn:
        db_conn.close()
        print("\nDatabase connection closed.")
atexit.register(close_db)

# --- INITIALIZATION ---
print("Loading the stork detection model...")
model = YOLO(MODEL_PATH)
os.makedirs(OUTPUT_DIR, exist_ok=True)
print("Model loaded. Starting real-time detection loop.")
print(f"A detection will run every {int(LOOP_INTERVAL_SECONDS / 60)} minute(s).")
print("Press Ctrl+C to stop the script.")

# --- MAIN LOOP ---
try:
    while True:
        print(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        print("Getting YouTube stream URL...")
        
        try:
            ydl_opts = {'format': 'best', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(YOUTUBE_URL, download=False)
                stream_url = info_dict.get('url', None)

            if not stream_url:
                print("Could not get stream URL. Retrying in the next cycle.")
                time.sleep(LOOP_INTERVAL_SECONDS)
                continue

            print("Opening stream with OpenCV to capture a frame...")
            cap = cv2.VideoCapture(stream_url)
            time.sleep(2)
            success, frame = cap.read() # This is the correct frame capture
            cap.release()

            if success:
                print("Frame captured. Running prediction...")
                results = model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, save=False, verbose=False)

                timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S')
                detection_count = len(results[0].boxes)
                
                image_filename = f'detection_{time.strftime("%Y%m%d_%H%M%S")}.jpg'
                output_path = os.path.join(OUTPUT_DIR, image_filename)
                cv2.imwrite(output_path, results[0].plot())
                
                cursor.execute(
                    "INSERT INTO detections (timestamp, stork_count, image_path) VALUES (?, ?, ?)",
                    (timestamp_str, detection_count, image_filename)
                )
                db_conn.commit()
                
                print(f"Found {detection_count} storks. Saved to database and image saved to {output_path}")
            else:
                print("Could not capture a frame from the stream.")
        
        except Exception as e:
            print(f"An error occurred in the detection cycle: {e}")

        print(f"Waiting {int(LOOP_INTERVAL_SECONDS / 60)} minute(s) for the next cycle...")
        time.sleep(LOOP_INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("\nScript stopped by user.")