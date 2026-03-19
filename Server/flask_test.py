from flask import Flask, request

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()

    print("\n--- Received Data ---")
    print(data)

    return {"status": "ok"}, 200


if __name__ == '__main__':
    print("Server starting...")
    app.run(host='0.0.0.0', port=5000)