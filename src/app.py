import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, jsonify, send_from_directory, send_file, request
from io import BytesIO

script_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(script_dir, '..'))
DB_FILE = os.path.join(PROJECT_ROOT, 'storks.db')
DETECTION_DIR = os.path.join(PROJECT_ROOT, 'runs/detect/realtime')
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

def query_db(query, args=(), one=False):
    if not os.path.exists(DB_FILE):
        return None
    
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    con.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/latest_detection')
def latest_detection():
    detections = query_db('SELECT image_path FROM detections ORDER BY timestamp DESC LIMIT 6')
    filenames = [row['image_path'] for row in detections] if detections else []
    return jsonify({'recent_files': filenames})

@app.route('/detections/<path:filename>')
def serve_detection_image(filename):
    return send_from_directory(DETECTION_DIR, filename)

@app.route('/detection_data')
def detection_data():
    detections = query_db("SELECT timestamp, stork_count FROM detections WHERE timestamp >= DATETIME('now', '-24 hours') ORDER BY timestamp ASC")
    if detections is None:
        return jsonify({'labels': [], 'data': []})
    chart_data = {
        'labels': [row['timestamp'] for row in detections],
        'data': [row['stork_count'] for row in detections],
    }
    return jsonify(chart_data)

@app.route('/hourly_activity')
def hourly_activity():
    detections = query_db("SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, AVG(stork_count) as avg_count FROM detections GROUP BY hour ORDER BY hour ASC")
    if detections is None:
        return jsonify({'labels': [], 'data': []})
    hourly_avg = {row['hour']: row['avg_count'] for row in detections}
    all_hours_data = [hourly_avg.get(h, 0) for h in range(24)]
    chart_data = {
        'labels': list(range(24)),
        'data': all_hours_data,
    }
    return jsonify(chart_data)

@app.route('/explorer')
def explorer():
    """Renders the data explorer page."""
    return render_template('data_explorer.html')

@app.route('/download_log')
def download_log():
    """
    Reads the entire 'detections' table, converts it to CSV,
    and sends it to the user for download using a binary buffer.
    """
    if not os.path.exists(DB_FILE):
        return "Error: Database file not found.", 404
        
    con = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * from detections", con)
    con.close()

    csv_buffer = BytesIO()
    
    csv_data = df.to_csv(index=False).encode('utf-8')
    csv_buffer.write(csv_data)
    csv_buffer.seek(0)
    
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='detections_log.csv'
    )

@app.route('/current_status')
def current_status():
    """
    API endpoint to get Key Performance Indicators (KPIs).
    """
    latest = query_db("SELECT timestamp, stork_count FROM detections ORDER BY timestamp DESC LIMIT 1", one=True)
    
    busiest = query_db("""
        SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour
        FROM detections
        GROUP BY hour
        ORDER BY AVG(stork_count) DESC, COUNT(id) DESC
        LIMIT 1
    """, one=True)

    if latest:
        current_count = latest['stork_count']
        nest_status = "Busy" if current_count > 0 else "Empty"
        last_seen = latest['timestamp'].split(' ')[1]
    else:
        current_count = "-"
        nest_status = "Desconocido"
        last_seen = "N/A"

    busiest_hour = f"{busiest['hour']}:00" if busiest else "N/A"

    status_data = {
        'current_count': current_count,
        'nest_status': nest_status,
        'last_seen': last_seen,
        'busiest_hour': busiest_hour
    }
    return jsonify(status_data)

@app.route('/daily_activity')
def daily_activity():
    """
    API endpoint for average daily activity over the last 7 days.
    """
    # Query for the last 7 days of data
    records = query_db("""
        SELECT 
            strftime('%Y-%m-%d', timestamp) as day, 
            AVG(stork_count) as avg_count
        FROM detections
        WHERE date(timestamp) >= date('now', '-6 days')
        GROUP BY day ORDER BY day ASC
    """)
    if records is None:
        return jsonify({'labels': [], 'data': []})

    # Prepare data for the last 7 days, filling missing days with 0
    today = pd.to_datetime('today').normalize()
    date_range = pd.date_range(start=today - pd.Timedelta(days=6), end=today, freq='D')
    
    # Create a DataFrame to easily merge the data
    df_dates = pd.DataFrame(date_range, columns=['day'])
    df_dates['day'] = df_dates['day'].dt.strftime('%Y-%m-%d')

    if records:
        df_records = pd.DataFrame(records, columns=['day', 'avg_count'])
        df_final = pd.merge(df_dates, df_records, on='day', how='left').fillna(0)
    else:
        df_final = df_dates
        df_final['avg_count'] = 0

    chart_data = {
        'labels': df_final['day'].tolist(),
        'data': df_final['avg_count'].round(2).tolist()
    }
    return jsonify(chart_data)


@app.route('/occupancy_status')
def occupancy_status():
    """
    API endpoint for nest occupancy status over the last 24 hours.
    """
    records = query_db("""
        SELECT
            SUM(CASE WHEN stork_count > 0 THEN 1 ELSE 0 END) as occupied_count,
            SUM(CASE WHEN stork_count = 0 THEN 1 ELSE 0 END) as empty_count
        FROM detections
        WHERE timestamp >= DATETIME('now', '-24 hours')
    """, one=True)

    if records is None or records['occupied_count'] is None:
        # Default to 0 if there's no data
        return jsonify({'labels': ['Busy', 'Empty'], 'data': [0, 0]})
        
    chart_data = {
        'labels': ['Busy', 'Empty'],
        'data': [records['occupied_count'], records['empty_count']]
    }
    return jsonify(chart_data)

@app.route('/all_data')
def all_data():
    """
    API endpoint to fetch all records from the database
    and format it for the DataTables library.
    """
    records = query_db("SELECT id, timestamp, stork_count, image_path FROM detections ORDER BY timestamp DESC")
    
    # The 'data' key is required by the DataTables library
    if records is None:
        return jsonify({'data': []})

    # Convert the list of Row objects to a list of dictionaries
    data_list = [dict(row) for row in records]
    
    return jsonify({'data': data_list})

@app.route('/query_data')
def query_data():
    """
    Securely queries the database based on filter parameters from the URL.
    """
    # Base query
    query = "SELECT id, timestamp, stork_count, image_path FROM detections WHERE 1=1"
    params = []

    # Get parameters from the request
    count = request.args.get('count')
    operator = request.args.get('operator', '>=') # Default to '>='
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Safely add conditions to the query
    if count:
        if operator in ['=', '>', '<', '>=', '<=']:
            query += f" AND stork_count {operator} ?"
            params.append(int(count))

    if start_date:
        query += " AND date(timestamp) >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND date(timestamp) <= ?"
        params.append(end_date)
    
    query += " ORDER BY timestamp DESC"

    records = query_db(query, params)
    
    if records is None:
        return jsonify({'data': []})

    data_list = [dict(row) for row in records]
    return jsonify({'data': data_list})

if __name__ == '__main__':
    app.run(debug=True)