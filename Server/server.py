from flask import Flask, request, jsonify, render_template
import time

app = Flask(__name__)

# Store received data
data_store = []

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if data:
        data['timestamp'] = time.strftime("%H:%M:%S")
        data_store.append(data)
        print("\n--- Received Data ---")
        print(data)
    return jsonify({"status": "ok"}), 200

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store)

@app.route('/')
def index():
    return render_template('index.html', data=data_store)

if __name__ == '__main__':
    print("Server starting...")
    app.run(host='0.0.0.0', port=5000)