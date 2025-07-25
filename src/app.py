# File: src/app.py
import os
import glob
import pandas as pd
from flask import Flask, render_template, jsonify, send_from_directory, send_file

# --- Path Definitions (The Correct Way) ---
script_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_ABSOLUTE = os.path.abspath(os.path.join(script_dir, '..'))
DETECTION_DIR = os.path.join(PROJECT_ROOT_ABSOLUTE, 'runs/detect/realtime')
TEMPLATE_DIR = os.path.join(PROJECT_ROOT_ABSOLUTE, 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT_ABSOLUTE, 'static')
# --- THIS LINE WAS MISSING ---
LOG_FILE = os.path.join(PROJECT_ROOT_ABSOLUTE, 'detections_log.csv')

# --- Flask App Initialization ---
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/latest_detection')
def latest_detection():
    """
    API endpoint to get the filenames of the 6 most recent detections.
    """
    if not os.path.isdir(DETECTION_DIR):
        return jsonify({'error': 'Detection directory not found'}), 404

    # Find all .jpg files
    list_of_files = glob.glob(os.path.join(DETECTION_DIR, '*.jpg'))
    if not list_of_files:
        return jsonify({'recent_files': []}) # Return an empty list if no files

    # Sort files by creation time, newest first
    sorted_files = sorted(list_of_files, key=os.path.getctime, reverse=True)
    
    # Get the last 6 filenames
    recent_filenames = [os.path.basename(f) for f in sorted_files[:6]]
    
    return jsonify({'recent_files': recent_filenames})


@app.route('/detections/<path:filename>')
def serve_detection_image(filename):
    return send_from_directory(DETECTION_DIR, filename)


@app.route('/detection_data')
def detection_data():
    """
    API endpoint to read the CSV log and return data FOR THE LAST 24 HOURS for the chart.
    """
    if not os.path.exists(LOG_FILE):
        return jsonify({'error': 'Log file not found'}), 404

    df = pd.read_csv(LOG_FILE)
    
    # --- NEW: Filter data for the last 24 hours ---
    # Convert the timestamp column to a proper datetime object
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    now = pd.Timestamp.now()
    cutoff = now - pd.Timedelta(hours=12)

    # Filter the dataframe
    df_filtered = df[df['timestamp'] > cutoff]
    # --- End of new filtering section ---

    # Convert the FILTERED dataframe to a dictionary format that Chart.js can use
    chart_data = {
        'labels': df_filtered['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'data': df_filtered['stork_count'].tolist(),
    }
    return jsonify(chart_data)

@app.route('/download_log')
def download_log():
    """
    This route sends the detections_log.csv file to the user for download.
    """
    # Use the LOG_FILE variable we already defined
    if not os.path.exists(LOG_FILE):
        return "Error: Log file not found.", 404
    
    return send_file(LOG_FILE, as_attachment=True)

@app.route('/hourly_activity')
def hourly_activity():
    """
    API endpoint to get the average stork count for each hour of the day.
    """
    if not os.path.exists(LOG_FILE):
        return jsonify({'error': 'Log file not found'}), 404

    try:
        df = pd.read_csv(LOG_FILE)
        if df.empty:
            return jsonify({'labels': [], 'data': []}) # Return empty data if log is empty

        # Convert timestamp to datetime and extract the hour
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour

        # Group by hour and calculate the average stork count
        hourly_avg = df.groupby('hour')['stork_count'].mean().round(2) # Round to 2 decimals

        # Create a complete list for all 24 hours, filling missing hours with 0
        all_hours = pd.Series([0.0] * 24, index=range(24))
        all_hours.update(hourly_avg)

        chart_data = {
            'labels': all_hours.index.tolist(), # Labels will be [0, 1, 2, ..., 23]
            'data': all_hours.values.tolist(),
        }
        return jsonify(chart_data)
    except Exception as e:
        print(f"Error processing hourly activity: {e}")
        return jsonify({'error': 'Could not process log file'}), 500

if __name__ == '__main__':
    app.run(debug=True)