from flask import Flask, request, jsonify, render_template
import time

app = Flask(__name__)

# Store received data (limit size for performance)
data_store = []
MAX_ENTRIES = 100


@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if data:
        data['timestamp'] = time.strftime("%H:%M:%S")

        data_store.append(data)

        # Keep only the latest MAX_ENTRIES
        if len(data_store) > MAX_ENTRIES:
            data_store.pop(0)

        print("\n--- Received Data ---")
        print(data)

    return jsonify({"status": "ok"}), 200


@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_store)


# 🏠 NEW HOME PAGE (graphs + alert)
@app.route('/')
def home():
    return render_template('home.html')


# 📋 DATA TABLE PAGE (your original dashboard)
@app.route('/data-view')
def data_view():
    return render_template('index.html')


if __name__ == '__main__':
    print("Server starting...")
    app.run(host='0.0.0.0', port=5000, debug=True)