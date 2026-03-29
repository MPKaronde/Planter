from flask import Flask, request, jsonify, render_template
import time
import csv
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# ----------------------------
# CONFIG
# ----------------------------
MAX_ENTRIES = 100
LOG_FILE = "data_log.csv"
SOLAR_THRESHOLD = 3.0  # V considered sunlight
READING_INTERVAL_SEC = 10  # Approximate interval between sensor posts for sunlight calculation

# ----------------------------
# IN-MEMORY DASHBOARD DATA
# ----------------------------
data_store = []

# Ensure CSV exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "device_name", "battery_voltage", "solar_voltage", "moisture_percentage"])

# Load last MAX_ENTRIES from CSV
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['battery_voltage'] = float(row['battery_voltage'])
                row['solar_voltage'] = float(row['solar_voltage'])
                row['moisture_percentage'] = float(row['moisture_percentage'])
                data_store.append(row)
            except (ValueError, TypeError):
                continue
    data_store = data_store[-MAX_ENTRIES:]

# ----------------------------
# ROUTES
# ----------------------------
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if data:
        # Use server timestamp
        data['timestamp'] = time.strftime("%H:%M:%S")
        data_store.append(data)
        if len(data_store) > MAX_ENTRIES:
            data_store.pop(0)

        # Save to CSV
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                data['timestamp'],
                data.get('device_name', ''),
                data.get('battery_voltage', ''),
                data.get('solar_voltage', ''),
                data.get('moisture_percentage', '')
            ])

    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store)

@app.route('/')
def index():
    return render_template('index.html')  # Home page with graphs

@app.route('/data-view')
def data_view():
    # Read all CSV rows safely
    all_data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                safe_row = {
                    "timestamp": row.get("timestamp", ""),
                    "device_name": row.get("device_name", ""),
                    "battery_voltage": row.get("battery_voltage", ""),
                    "solar_voltage": row.get("solar_voltage", ""),
                    "moisture_percentage": row.get("moisture_percentage", "")
                }
                all_data.append(safe_row)
    return render_template('data.html', data=all_data)

@app.route('/sunlight-data')
def sunlight_data():
    """Compute hours of sunlight today and last 7 days"""
    sunlight_counts = {}  # date_str -> number of sunlight readings
    now = datetime.now()

    last_7_days = [(now - timedelta(days=i)).date() for i in reversed(range(7))]

    for row in data_store:
        try:
            solar = float(row['solar_voltage'])
        except (ValueError, TypeError):
            continue
        ts = datetime.now().date()  # Use server timestamp as date

        # Count sunlight if above threshold
        if solar >= SOLAR_THRESHOLD:
            sunlight_counts[ts] = sunlight_counts.get(ts, 0) + 1

    # Convert counts to hours
    sunlight_hours = {day.strftime("%Y-%m-%d"): sunlight_counts.get(day, 0) * READING_INTERVAL_SEC / 3600 for day in last_7_days}

    return jsonify({
        "today_hours": sunlight_hours.get(now.strftime("%Y-%m-%d"), 0),
        "weekly": sunlight_hours
    })

# ----------------------------
# START SERVER
# ----------------------------
if __name__ == '__main__':
    print("Server starting...")
    app.run(host='0.0.0.0', port=5000)