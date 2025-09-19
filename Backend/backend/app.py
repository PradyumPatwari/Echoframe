import os
import time
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
from flask_cors import CORS

# Load local .env for development only
load_dotenv()

# Flask setup
app = Flask(__name__)
# Allow all origins for now; replace with specific origin for production if you have one
CORS(app, supports_credentials=True)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("echoframe-backend")

# Reality Defender config
API_KEY = os.getenv("REALITY_DEFENDER_API_KEY")
HEADERS = {"x-api-key": API_KEY} if API_KEY else {}
BASE_URL = "https://api.realitydefender.com/v1"
REQUEST_TIMEOUT = 15  # seconds


@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "message": "✅ EchoFrame backend is live"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


def poll_scan(scan_id, retries=10, wait=3):
    """Poll Reality Defender until scan is finished or retries exhausted."""
    poll_url = f"{BASE_URL}/scans/{scan_id}"
    last = {}
    for _ in range(retries):
        try:
            resp = requests.get(poll_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            last = data
            if data.get("status") in ("done", "success"):
                return data
        except requests.RequestException as e:
            logger.warning(f"poll_scan request error: {e}")
        time.sleep(wait)
    return last


def normalize(rd_data, media_url):
    """Make a small normalized response for frontend."""
    score = rd_data.get("score")
    label = rd_data.get("label")
    if not score and "detections" in rd_data:
        detections = rd_data["detections"]
        if isinstance(detections, list) and detections:
            score = detections[0].get("confidence", 0)
            label = detections[0].get("label", "unknown")
    try:
        score = float(score)
    except Exception:
        score = 0.0
    label = label or "unknown"
    ai_usage = rd_data.get("ai_usage", max(0, 100 - int(score if score else 0)))
    return {
        "label": label,
        "mediaUrl": media_url,
        "score": score,
        "ai_usage": ai_usage,
        "status": rd_data.get("status", "unknown"),
        "raw": rd_data,
    }


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze a public media URL. JSON body: { "mediaUrl": "https://..." }"""
    if not API_KEY:
        return jsonify({"error": "REALITY_DEFENDER_API_KEY not configured"}), 500

    data = request.get_json(silent=True) or {}
    media_url = data.get("mediaUrl")
    if not media_url:
        return jsonify({"error": "mediaUrl is required"}), 400

    logger.info(f"Analyze URL requested: {media_url}")
    try:
        resp = requests.post(
            f"{BASE_URL}/scan/url",
            headers=HEADERS,
            json={"url": media_url},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        rd_data = resp.json()
        # If queued -> poll
        if rd_data.get("status") == "pending" and rd_data.get("id"):
            rd_data = poll_scan(rd_data["id"])
        normalized = normalize(rd_data, media_url)
        return jsonify(normalized), 200
    except requests.RequestException as e:
        logger.exception("Reality Defender request failed")
        return jsonify({"error": "Failed to analyze media", "detail": str(e)}), 502


@app.route("/analyze-file", methods=["POST"])
def analyze_file():
    """Analyze uploaded file (form field name: file)"""
    if not API_KEY:
        return jsonify({"error": "REALITY_DEFENDER_API_KEY not configured"}), 500

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded (field name must be 'file')"}), 400

    file = request.files["file"]
    filename = file.filename or "uploaded_media"
    logger.info(f"Analyze file requested: {filename}")

    try:
        # send file as streaming to Reality Defender
        files = {"file": (filename, file.stream, file.mimetype)}
        resp = requests.post(
            f"{BASE_URL}/scan/file",
            headers=HEADERS,
            files=files,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        rd_data = resp.json()
        if rd_data.get("status") == "pending" and rd_data.get("id"):
            rd_data = poll_scan(rd_data["id"])
        normalized = normalize(rd_data, filename)
        return jsonify(normalized), 200
    except requests.RequestException as e:
        logger.exception("Reality Defender file scan failed")
        return jsonify({"error": "Failed to analyze file", "detail": str(e)}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # debug=False for production; can use debug=True locally
    app.run(host="0.0.0.0", port=port, debug=False)
