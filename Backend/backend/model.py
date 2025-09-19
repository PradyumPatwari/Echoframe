# model.py
import tensorflow as tf
from tensorflow.keras import layers, models

def build_cnn_rnn_model(input_shape=(30, 128, 128, 3)):  
    """
    CNN + RNN model for deepfake detection.
    input_shape: (frames, height, width, channels)
    """

    frames, h, w, c = input_shape

    model = models.Sequential()

    # CNN feature extractor (applied to each frame)
    cnn_base = tf.keras.Sequential([
        layers.Conv2D(32, (3,3), activation='relu', input_shape=(h,w,c)),
        layers.MaxPooling2D((2,2)),
        layers.Conv2D(64, (3,3), activation='relu'),
        layers.MaxPooling2D((2,2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu')
    ])

    # Apply CNN to sequence of frames
    model.add(layers.TimeDistributed(cnn_base, input_shape=input_shape))

    # RNN to learn temporal features
    model.add(layers.LSTM(64, return_sequences=False))
    model.add(layers.Dense(1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model
