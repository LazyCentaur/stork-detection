# File: realtime_detector.py
import cv2
import time
from ultralytics import YOLO
import yt_dlp
import os
import csv
import pandas as pd # Import pandas

# --- CONFIGURATION ---
MODEL_PATH = 'runs/detect/stork_experiment_1/weights/best.pt'
YOUTUBE_URL = 'https://www.youtube.com/watch?v=i_jiHI3k8ag'
CONFIDENCE_THRESHOLD = 0.5
LOOP_INTERVAL_SECONDS = 600 # 10 minutes
OUTPUT_DIR = 'runs/detect/realtime'
LOG_FILE = 'detections_log.csv'
ARCHIVE_FILE = 'detections_archive.csv' # NEW: Archive file

# --- NEW: Cleanup Function ---
def cleanup_log_file():
    print("Running log cleanup...")
    if not os.path.exists(LOG_FILE):
        print("Log file not found, nothing to clean.")
        return

    try:
        df = pd.read_csv(LOG_FILE)
        if df.empty:
            print("Log file is empty.")
            return

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        now = pd.Timestamp.now()
        cutoff = now - pd.Timedelta(hours=12)
        
        old_data = df[df['timestamp'] <= cutoff]
        recent_data = df[df['timestamp'] > cutoff]
        
        if not old_data.empty:
            print(f"Archiving {len(old_data)} old records...")
            # Append old data to the archive file (with header if file is new)
            old_data.to_csv(ARCHIVE_FILE, mode='a', header=not os.path.exists(ARCHIVE_FILE), index=False)
            
            # Overwrite the log file with only the recent data
            recent_data.to_csv(LOG_FILE, index=False)
            print("Cleanup complete.")
        else:
            print("No old records to archive.")
    except Exception as e:
        print(f"Error during log cleanup: {e}")


# --- INITIALIZATION ---
print("Loading the stork detection model...")
model = YOLO(MODEL_PATH)
os.makedirs(OUTPUT_DIR, exist_ok=True)
# ... (rest of the initialization code is the same) ...

# --- MAIN LOOP ---
try:
    while True:
        # --- Run the cleanup at the beginning of each loop ---
        cleanup_log_file()

        print(f"\n--- {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        # ... (the rest of your loop code for detection and saving remains the same) ...
        # ...
        
        # --- WAIT ---
        print(f"Waiting {int(LOOP_INTERVAL_SECONDS / 60)} minute(s) for the next cycle...")
        time.sleep(LOOP_INTERVAL_SECONDS)

except KeyboardInterrupt:
    print("\nScript stopped by user. Goodbye!")