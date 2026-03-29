from flask import Flask, request, jsonify, render_template
import time
import csv
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

DATA_FILE = "data_log.csv"
ALERT_RECIPIENTS = ["friend@example.com"]  # put recipient emails here
MOISTURE_THRESHOLD = 30  # moisture % to trigger alert

# Load existing data from CSV at startup
data_store = []
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data_store.append({
                "timestamp": row["timestamp"],
                "device_name": row["device_name"],
                "battery_voltage": float(row["battery_voltage"]),
                "solar_voltage": float(row["solar_voltage"]),
                "moisture_percentage": float(row["moisture_percentage"])
            })

# ---------------------- EMAIL ALERT FUNCTION ----------------------
def send_moisture_alert(device_name, moisture_value):
    msg = EmailMessage()
    msg['Subject'] = f"⚠️ Moisture Alert for {device_name}"
    msg['From'] = "yourpotemail@gmail.com"  # must match msmtp config
    msg['To'] = ", ".join(ALERT_RECIPIENTS)
    msg.set_content(f"Moisture level is too low: {moisture_value}%.\nPlease check your plant!")

    try:
        with smtplib.SMTP('localhost') as smtp:
            smtp.send_message(msg)
        print(f"Sent alert email for {device_name}")
        with open("alerts.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Moisture alert sent for {device_name}\n")
    except Exception as e:
        print("Error sending email:", e)

# ---------------------- ROUTES ----------------------
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if data:
        # Add server timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "device_name": data.get("device_name", "Unknown"),
            "battery_voltage": float(data.get("battery_voltage", 0)),
            "solar_voltage": float(data.get("solar_voltage", 0)),
            "moisture_percentage": float(data.get("moisture_percentage", 0))
        }
        data_store.append(entry)

        # Save to CSV
        file_exists = os.path.exists(DATA_FILE)
        with open(DATA_FILE, "a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(entry)

        # Check moisture and send alert
        if entry["moisture_percentage"] < MOISTURE_THRESHOLD:
            send_moisture_alert(entry["device_name"], entry["moisture_percentage"])

        print("\n--- Received Data ---")
        print(entry)

    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/data-view')
def data_view():
    return render_template('data.html', data=data_store)

if __name__ == '__main__':
    print("Server starting...")
    app.run(host='0.0.0.0', port=5000)