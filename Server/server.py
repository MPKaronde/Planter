from flask import Flask, request, jsonify, render_template
import time
import csv
import os
import datetime
import subprocess

app = Flask(__name__)

# In-memory storage of recent data
data_store = []

# CSV for long-term storage
CSV_FILE = "plant_data.csv"

# Moisture thresholds
MOISTURE_TOO_LOW = 30
MOISTURE_WARNING = 40
MOISTURE_OK_HIGH = 70

# Email cooldown (minutes) to prevent spamming
EMAIL_COOLDOWN = 5
last_alert_time = {}

# --- Configure your emails here ---
SENDER_EMAIL = "basillybarry@gmail.com"        # Gmail configured with msmtp
RECIPIENT_EMAIL = "karonde.manav@gmail.com"      # Email to receive alerts

# Ensure CSV exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "device_name", "battery_voltage", "solar_voltage", "moisture_percentage"])

# --- Email function using msmtp subprocess ---
def send_moisture_alert(device_name, moisture_value):
    sender = "basillybarry@gmail.com"
    recipients = ["karonde.manav@gmail.com", "pratap.karonde@gmail.com", "rashmithk@gmail.com"]  # Add as many as you like
    subject = f"⚠️ Moisture Alert for {device_name}"
    body = f"Moisture level for {device_name} is too low: {moisture_value}%."

    # Create comma-separated string for the email header
    to_header = ", ".join(recipients)

    # Full email with headers
    email_content = f"From: {sender}\nTo: {to_header}\nSubject: {subject}\n\n{body}"

    # Send via msmtp to all recipients
    for recipient in recipients:
        try:
            subprocess.run(f'echo "{email_content}" | msmtp {recipient}', shell=True, check=True)
            print(f"[EMAIL SENT] {device_name} moisture {moisture_value}% to {recipient}")
        except subprocess.CalledProcessError as e:
            print("[EMAIL ERROR]", e)

# --- Routes ---
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "device_name": data.get("device_name", "Unknown"),
        "battery_voltage": float(data.get("battery_voltage", 0)),
        "solar_voltage": float(data.get("solar_voltage", 0)),
        "moisture_percentage": float(data.get("moisture_percentage", 0))
    }

    # Store in memory
    data_store.append(entry)

    # Append to CSV
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            entry["timestamp"], entry["device_name"], entry["battery_voltage"],
            entry["solar_voltage"], entry["moisture_percentage"]
        ])

    print("[DATA RECEIVED]", entry)

    # --- Moisture alert with cooldown ---
    device = entry["device_name"]
    now = datetime.datetime.now()
    send_alert = False

    if entry["moisture_percentage"] < MOISTURE_TOO_LOW:
        if device not in last_alert_time:
            send_alert = True
        else:
            elapsed = (now - last_alert_time[device]).total_seconds() / 60
            if elapsed >= EMAIL_COOLDOWN:
                send_alert = True
        if send_alert:
            print(f"[ALERT TRIGGER] {device} moisture {entry['moisture_percentage']}%")
            send_moisture_alert(device, entry["moisture_percentage"])
            last_alert_time[device] = now

    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store)

@app.route('/data-view')
def data_view():
    # Load CSV for long-term display
    csv_data = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_data.append(row)
    return render_template("data.html", data=csv_data)

@app.route('/')
def index():
    return render_template('home.html', data=data_store)

@app.route('/sunlight-data')
def sunlight_data():
    # Dummy example data
    weekly = {f"Day {i+1}": round(5 + i*0.5,1) for i in range(7)}
    today_hours = 6.5
    return jsonify({"weekly": weekly, "today_hours": today_hours})

if __name__ == '__main__':
    print("Server starting...")
    app.run(host='0.0.0.0', port=5000)