from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
from tensorflow.keras import layers, models

app = Flask(__name__)
CORS(app)

# -------------------------
# Build a simple CNN + RNN model
# -------------------------
def build_cnn_rnn_model(input_shape=(30, 128, 128, 3)):
    frames, h, w, c = input_shape

    model = models.Sequential()

    # CNN feature extractor
    cnn_base = models.Sequential([
        layers.Conv2D(32, (3,3), activation='relu', input_shape=(h,w,c)),
        layers.MaxPooling2D((2,2)),
        layers.Conv2D(64, (3,3), activation='relu'),
        layers.MaxPooling2D((2,2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu')
    ])

    # Apply CNN to sequence of frames
    model.add(layers.TimeDistributed(cnn_base, input_shape=input_shape))

    # RNN for temporal features
    model.add(layers.LSTM(64, return_sequences=False))
    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Load model (fresh each time – ideally load pretrained weights here)
model = build_cnn_rnn_model()

# -------------------------
# API Endpoint
# -------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    url = data.get("url", None)

    if not url:
        return jsonify({"error": "url is required"}), 400

    # ⚡ Dummy preprocessing: simulate 30 frames of size 128x128x3
    # In a real case: download the video/image, extract frames with cv2.VideoCapture
    frames = np.random.rand(30, 128, 128, 3).astype(np.float32)

    frames = np.expand_dims(frames, axis=0)  # (1, 30, 128, 128, 3)

    # Predict (real/fake probability)
    prediction = model.predict(frames, verbose=0)[0][0]

    result = {
        "status": "success",
        "mediaUrl": url,
        "score": round(float(prediction) * 100, 2),  # confidence %
        "label": "Real" if prediction > 0.5 else "Fake"
    }

    return jsonify(result)

# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)
