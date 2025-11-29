# tools/xray_mock_server.py
from flask import Flask, request, jsonify
import uuid, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=5001)
args, _ = parser.parse_known_args()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return 'XRAY mock running', 200

@app.route('/xray/executions', methods=['POST'])
def create_exec():
    payload = request.get_json() or {}
    return jsonify({'execution_id': f'EXEC-{uuid.uuid4().hex[:8]}', 'status':'received'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=args.port)