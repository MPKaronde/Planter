from flask import Flask, request, jsonify, render_template
import time
import csv
import os

app = Flask(__name__)

# ----------------------------
# CONFIG
# ----------------------------
MAX_ENTRIES = 100
LOG_FILE = "data_log.csv"

# ----------------------------
# DATA STORE (in-memory for dashboard)
# ----------------------------
data_store = []

# Ensure CSV file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "device_name", "battery_voltage", "solar_voltage", "moisture_percentage"])

# Load last MAX_ENTRIES for dashboard
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

        print("\n--- Received Data ---")
        print(data)

    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store)

@app.route('/')
def index():
    return render_template('index.html')  # Home page with graphs and alert banner

@app.route('/data-view')
def data_view():
    # Read all CSV rows safely
    all_data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Keep as string for display; avoids template crashes
                safe_row = {
                    "timestamp": row.get("timestamp", ""),
                    "device_name": row.get("device_name", ""),
                    "battery_voltage": row.get("battery_voltage", ""),
                    "solar_voltage": row.get("solar_voltage", ""),
                    "moisture_percentage": row.get("moisture_percentage", "")
                }
                all_data.append(safe_row)
    return render_template('data.html', data=all_data)

# ----------------------------
# START SERVER
# ----------------------------
if __name__ == '__main__':
    print("Server starting...")
    app.run(host='0.0.0.0', port=5000)