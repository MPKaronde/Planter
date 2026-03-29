from flask import Flask, request, jsonify, render_template
import time
import csv
import os
import datetime
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# Store received data in memory
data_store = []

# CSV file for long-term storage
CSV_FILE = "plant_data.csv"

# Moisture thresholds
MOISTURE_TOO_LOW = 30  # below this -> alert
MOISTURE_WARNING = 40  # between warning and low
MOISTURE_OK_HIGH = 70  # above this -> too wet

# Email cooldown per device (minutes)
EMAIL_COOLDOWN = 30
last_alert_time = {}

# Ensure CSV exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "device_name", "battery_voltage", "solar_voltage", "moisture_percentage"])

# --- Email sending function ---
def send_moisture_alert(device_name, moisture_value):
    msg = EmailMessage()
    msg['Subject'] = f"⚠️ Moisture Alert for {device_name}"
    msg['From'] = "yourpotemail@gmail.com"       # Replace with your sender email
    msg['To'] = "recipient@example.com"          # Replace with recipient email
    msg.set_content(f"Moisture level for {device_name} is too low: {moisture_value}%.")

    try:
        with smtplib.SMTP('localhost') as smtp:   # Uses msmtp configured on Raspberry Pi
            smtp.send_message(msg)
        print(f"[EMAIL SENT] {device_name} moisture {moisture_value}%")
    except Exception as e:
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

    data_store.append(entry)

    # Append to CSV
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            entry["timestamp"], entry["device_name"], entry["battery_voltage"],
            entry["solar_voltage"], entry["moisture_percentage"]
        ])

    print("[DATA RECEIVED]", entry)

    # Check moisture for email alert
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
    # Load CSV data for display
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

# --- Sunlight placeholder endpoint ---
@app.route('/sunlight-data')
def sunlight_data():
    # Example dummy data; replace with real calculation if you have solar sensor data
    weekly = {f"Day {i+1}": round(5 + i*0.5,1) for i in range(7)}  # 7 days sunlight hours
    today_hours = 6.5
    return jsonify({"weekly": weekly, "today_hours": today_hours})

if __name__ == '__main__':
    print("Server starting...")
    app.run(host='0.0.0.0', port=5000)