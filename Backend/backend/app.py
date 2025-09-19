import os
import time
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
CORS(app)

# Logger setup
logging.basicConfig(level=logging.INFO)

# Reality Defender API
API_KEY = os.getenv("REALITY_DEFENDER_API_KEY")
HEADERS = {"x-api-key": API_KEY}
BASE_URL = "https://api.realitydefender.com/v1"


def poll_scan(scan_id):
    """Poll Reality Defender until scan is finished"""
    poll_url = f"{BASE_URL}/scans/{scan_id}"
    for _ in range(10):  # try max 10 times (~30s)
        resp = requests.get(poll_url, headers=HEADERS)
        data = resp.json()
        if data.get("status") == "done":
            return data
        time.sleep(3)
    return data  # return last state (even if still pending)


def normalize(rd_data, media_url):
    """Normalize Reality Defender response into simple JSON"""
    score = rd_data.get("score")
    label = rd_data.get("label")

    # Fallback if missing
    if not score and "detections" in rd_data:
        detections = rd_data["detections"]
        if isinstance(detections, list) and detections:
            score = detections[0].get("confidence", 0)
            label = detections[0].get("label", "Unknown")

    score = score if isinstance(score, (int, float)) else 0
    label = label or "Unknown"
    ai_usage = rd_data.get("ai_usage", 100 - score)

    return {
        "label": label,
        "mediaUrl": media_url,
        "score": score,
        "ai_usage": ai_usage,
        "status": rd_data.get("status", "success"),
        "raw": rd_data
    }


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze a media URL"""
    data = request.get_json()
    media_url = data.get("mediaUrl") if data else None

    if not media_url:
        return jsonify({"error": "mediaUrl is required"}), 400

    logging.info(f"Analyzing URL: {media_url}")

    try:
        resp = requests.post(f"{BASE_URL}/scan/url", json={"url": media_url}, headers=HEADERS)
        resp.raise_for_status()
        rd_data = resp.json()

        # If scan is queued → poll until ready
        if rd_data.get("status") == "pending" and rd_data.get("id"):
            rd_data = poll_scan(rd_data["id"])

        normalized = normalize(rd_data, media_url)
        logging.info(f"Result: {normalized}")
        return jsonify(normalized)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Reality Defender API: {e}")
        return jsonify({"error": "Failed to analyze media."}), 500


@app.route("/analyze-file", methods=["POST"])
def analyze_file():
    """Analyze an uploaded media file"""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    logging.info(f"Analyzing uploaded file: {file.filename}")

    try:
        resp = requests.post(f"{BASE_URL}/scan/file", files={"file": file}, headers=HEADERS)
        resp.raise_for_status()
        rd_data = resp.json()

        # If scan is queued → poll until ready
        if rd_data.get("status") == "pending" and rd_data.get("id"):
            rd_data = poll_scan(rd_data["id"])

        normalized = normalize(rd_data, file.filename)
        logging.info(f"Result: {normalized}")
        return jsonify(normalized)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Reality Defender API: {e}")
        return jsonify({"error": "Failed to analyze file."}), 500


if __name__ == "__main__":  
    app.run(debug=True, port=5000)
