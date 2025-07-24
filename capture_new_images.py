# File: capture_new_images.py
import cv2
import time
from ultralytics import YOLO
import yt_dlp
import os

# --- Configuration ---
YOUTUBE_URL = 'https://www.youtube.com/live/i_jiHI3k8ag?si=I9UdrsND8z1lp_33'
# The folder where new raw images will be saved
OUTPUT_DIR = 'data/new_raw_images'
# How many new images you want to capture
FRAMES_TO_CAPTURE = 150
# Time in seconds to wait between each capture
CAPTURE_INTERVAL_SECONDS = 15 # 15 seconds to get more variety

# --- Initialization ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
print("Starting capture process...")
print(f"Will capture {FRAMES_TO_CAPTURE} new images, one every {CAPTURE_INTERVAL_SECONDS} seconds.")
print("Press Ctrl+C to stop the script early.")

# --- Main Capture Loop ---
try:
    print("Getting YouTube stream URL...")
    ydl_opts = {'format': 'best', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(YOUTUBE_URL, download=False)
        stream_url = info_dict.get('url', None)

    if not stream_url:
        raise ValueError("Could not get the stream URL.")

    cap = cv2.VideoCapture(stream_url)
    frames_captured = 0
    time.sleep(2)

    while cap.isOpened() and frames_captured < FRAMES_TO_CAPTURE:
        # --- This loop reads and discards frames for the interval period ---
        # This ensures you get a new, different image each time
        start_time = time.time()
        while time.time() - start_time < CAPTURE_INTERVAL_SECONDS:
            cap.grab() # Grab a frame but don't process it

        # --- Now, capture the real frame ---
        success, frame = cap.read()

        if success:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(OUTPUT_DIR, f'occlusion_frame_{timestamp}.jpg')
            cv2.imwrite(output_path, frame)
            frames_captured += 1
            print(f"({frames_captured}/{FRAMES_TO_CAPTURE}) Image saved to: {output_path}")
        else:
            print("Failed to capture frame. Re-establishing connection...")
            # Re-initialize connection if it fails
            cap.release()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(YOUTUBE_URL, download=False)
                stream_url = info_dict.get('url', None)
            if stream_url:
                cap = cv2.VideoCapture(stream_url)
            else:
                print("Could not re-establish connection. Exiting.")
                break

except KeyboardInterrupt:
    print("\nScript stopped by user.")
finally:
    if 'cap' in locals() and cap.isOpened():
        cap.release()
    print("Capture process finished.")