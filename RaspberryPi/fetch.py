# fetch.py
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

received_data = None  # Global variable to store the data

@app.route('/', methods=['POST'])
def home():
    return jsonify({"message": "Server Started!"})

@app.route('/submit-data', methods=['POST'])
def submit_data():
    global received_data
    print(request)
    try:
        data = request.json
        print(data)
        received_data = data
        print(f"Received data: {data}")
        return jsonify({"success": True, "message": "Data received successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def get_data():
    global received_data
    return received_data

def run_server():
    app.run(host='localhost', port=8000, debug=False)
    
#run_server()
