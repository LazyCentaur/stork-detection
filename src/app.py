# File: src/app.py
import os
import glob
import pandas as pd
from flask import Flask, render_template, jsonify, send_from_directory

# --- Path Definitions (The Correct Way) ---
# Get the absolute path of the directory where this script is located (src/)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root path by going one level up from 'src'
PROJECT_ROOT_ABSOLUTE = os.path.abspath(os.path.join(script_dir, '..'))

# Define all other paths relative to the project root
DETECTION_DIR = os.path.join(PROJECT_ROOT_ABSOLUTE, 'runs/detect/realtime')
TEMPLATE_DIR = os.path.join(PROJECT_ROOT_ABSOLUTE, 'templates')
LOG_FILE = os.path.join(PROJECT_ROOT_ABSOLUTE, 'detections_log.csv')

# --- Flask App Initialization ---
# Tell Flask where to find the templates folder using an absolute path
app = Flask(__name__, template_folder=TEMPLATE_DIR)


@app.route('/')
def index():
    """Renders the main web page."""
    return render_template('index.html')


@app.route('/latest_detection')
def latest_detection():
    """API endpoint to get the FILENAME of the most recent detection."""
    if not os.path.isdir(DETECTION_DIR):
        return jsonify({'error': 'Detection directory not found'}), 404

    list_of_files = glob.glob(os.path.join(DETECTION_DIR, '*.jpg'))
    if not list_of_files:
        return jsonify({'error': 'No detection images found'}), 404

    latest_file = max(list_of_files, key=os.path.getctime)
    filename = os.path.basename(latest_file)
    return jsonify({'filename': filename})


@app.route('/detections/<path:filename>')
def serve_detection_image(filename):
    """Serves the image file to the browser."""
    return send_from_directory(DETECTION_DIR, filename)


@app.route('/detection_data')
def detection_data():
    """API endpoint to read the CSV log and return data for the chart."""
    if not os.path.exists(LOG_FILE):
        return jsonify({'error': 'Log file not found'}), 404

    # Read the CSV data using pandas
    df = pd.read_csv(LOG_FILE)
    
    # Convert the dataframe to a dictionary format that Chart.js can use
    chart_data = {
        'labels': df['timestamp'].tolist(),
        'data': df['stork_count'].tolist(),
    }
    return jsonify(chart_data)


if __name__ == '__main__':
    app.run(debug=True)