from flask import Flask, request, jsonify, render_template
import time
import csv
import os

app = Flask(__name__)

MAX_ENTRIES = 100
LOG_FILE = "data_log.csv"

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
            except ValueError:
                continue
    data_store = data_store[-MAX_ENTRIES:]

# ----------------------------
# Routes
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
    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store)

@app.route('/')
def index():
    return render_template('index.html')  # Graphs + alert banner

@app.route('/data-view')
def data_view():
    # Read all CSV rows
    all_data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_data.append(row)
    return render_template('data.html', data=all_data)

# ----------------------------
# Start server
# ----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)