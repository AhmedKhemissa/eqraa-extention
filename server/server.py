# server.py
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from arabic_analyzer import fetch_word_data

load_dotenv()  # Load .env before other imports

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False  # Enable UTF-8 encoding for JSON responses

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/analyze', methods=['POST'])
@limiter.limit("10/minute")
def analyze():
    if not request.json or 'word' not in request.json:
        return jsonify({"error": "Missing 'word' parameter"}), 400
    
    word = request.json['word'].strip()
    try:
        result = fetch_word_data(word)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)