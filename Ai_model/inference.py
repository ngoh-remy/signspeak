"""
SignSpeak - MobileNetV2 Inference Module
=========================================
Replaces the old MediaPipe + LSTM approach entirely.

How this works (majority voting):
  1. The frontend sends video frames via WebSocket (same as before).
  2. For each received frame:
     - Resize to 64x64 grayscale
     - Convert to 3-channel RGB (MobileNetV2 expects 3 channels)
     - Run MobileNetV2.predict() → probability vector for each class
     - Add to a rolling vote buffer (last N_VOTES frame predictions)
  3. After N_VOTES frames are accumulated, sum all probability vectors.
  4. The class with the highest total score wins.
  5. If the winning confidence is above CONFIDENCE_THRESHOLD, emit prediction.
  6. Buffer resets (for UX progress bar) after a confident prediction.

Why this is better than LSTM + MediaPipe:
  - No MediaPipe dependency → no timestamp crashes → no freezing
  - Frame-by-frame prediction → consistent timing, no 30-frame wait
  - Majority voting → robust against bad/blurry frames
  - Transfer learning → works well on smaller datasets
  - Per-frame inference takes ~30ms on CPU vs ~400ms for MediaPipe
"""

import os
import cv2
import json
import pickle
import numpy as np
from collections import deque
from typing import Optional, Tuple

# ─── Configuration ────────────────────────────────────────────────────────────

MODEL_PATH   = os.path.join(os.path.dirname(__file__), "best_model.keras")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder.pkl")

IMG_SIZE     = 64    # Must match training: 64×64
N_VOTES      = 20    # Accumulate 20 frame predictions before deciding (~2 seconds at 10 FPS)
CONFIDENCE_THRESHOLD = 0.60  # Require 60% of accumulated vote probability to emit

# ─── Dependency Checks ────────────────────────────────────────────────────────

SIMULATION_MODE   = False
SIMULATION_REASON = ""

try:
    import numpy as np
except ImportError:
    SIMULATION_MODE   = True
    SIMULATION_REASON = "numpy not installed"

try:
    import cv2
except ImportError:
    cv2 = None
    SIMULATION_MODE   = True
    SIMULATION_REASON = "opencv not installed"


class SignRecognizer:
    """
    Real-time sign language recognizer using MobileNetV2 + majority voting.
    No MediaPipe. No LSTM sequences. No timestamp issues.
    """

    def __init__(self):
        self.model         = None
        self.label_encoder = None
        self.labels        = []
        self.vote_buffer   = deque(maxlen=N_VOTES)  # Rolling window of probability vectors
        self._loaded       = False

    def load(self):
        """Load model and label encoder. Called once at server startup."""
        if self._loaded:
            return

        global SIMULATION_MODE, SIMULATION_REASON

        if SIMULATION_MODE:
            print(f"[* WARNING *] SignSpeak starting in SIMULATION MODE: {SIMULATION_REASON}")
            self.labels  = ["hello", "thank you", "please", "yes", "no", "help", "sorry", "love", "good", "bad"]
            self._loaded = True
            return

        if not os.path.exists(MODEL_PATH):
            print(f"[* INFO *] best_model.keras not found at {MODEL_PATH}. Activating Simulation Mode.")
            SIMULATION_MODE   = True
            SIMULATION_REASON = "best_model.keras not found — run retrain_mobilenet.py first"
            self.labels  = ["hello", "thank you", "please", "yes", "no"]
            self._loaded = True
            return

        if not os.path.exists(ENCODER_PATH):
            print(f"[* INFO *] label_encoder.pkl not found at {ENCODER_PATH}. Activating Simulation Mode.")
            SIMULATION_MODE   = True
            SIMULATION_REASON = "label_encoder.pkl not found — run retrain_mobilenet.py first"
            self.labels  = ["hello", "thank you", "please", "yes", "no"]
            self._loaded = True
            return

        try:
            from tensorflow.keras.models import load_model as keras_load
            self.model = keras_load(MODEL_PATH, compile=False)
            print(f"[+] MobileNetV2 model loaded: {MODEL_PATH}")

            with open(ENCODER_PATH, "rb") as f:
                self.label_encoder = pickle.load(f)
            self.labels = list(self.label_encoder.classes_)
            print(f"[+] Label encoder loaded: {len(self.labels)} classes")
            print(f"[+] Classes: {self.labels}")

            self._loaded = True

        except Exception as e:
            print(f"[* WARNING *] Failed to load model: {e}. Activating Simulation Mode.")
            SIMULATION_MODE   = True
            SIMULATION_REASON = f"Model load error: {str(e)}"
            self.labels  = ["hello", "thank you", "please", "yes", "no"]
            self._loaded = True

    def process_frame(self, frame_bytes: bytes) -> Optional[Tuple[str, float]]:
        """
        Process one JPEG frame. Add its per-class probabilities to the vote buffer.
        Once N_VOTES frames are accumulated, perform majority voting and return
        a prediction if confident enough.

        Args:
            frame_bytes: Raw JPEG bytes from the frontend webcam.

        Returns:
            (sign_label, confidence) if a confident prediction is ready, else None.
        """
        if not self._loaded:
            self.load()

        if SIMULATION_MODE:
            self.vote_buffer.append(1)
            if len(self.vote_buffer) < N_VOTES:
                return None
            self.vote_buffer.clear()
            import random
            return random.choice(self.labels), random.uniform(0.75, 0.99)

        if cv2 is None:
            return None

        try:
            # Decode JPEG → numpy
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                return None

            # Resize to 64×64 grayscale, then convert to 3-channel RGB
            gray      = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray      = cv2.resize(gray, (IMG_SIZE, IMG_SIZE))
            gray_norm = gray.astype(np.float32) / 255.0
            rgb       = np.repeat(gray_norm.reshape(IMG_SIZE, IMG_SIZE, 1), 3, axis=-1)
            batch     = np.expand_dims(rgb, axis=0)  # Shape: (1, 64, 64, 3)

            # Run MobileNetV2 — fast! (~30ms on CPU)
            probs = self.model.predict(batch, verbose=0)[0]  # Shape: (N_CLASSES,)
            self.vote_buffer.append(probs)

            # Wait until we have N_VOTES frames before deciding
            if len(self.vote_buffer) < N_VOTES:
                return None

            # Majority voting: sum all probability vectors
            votes         = np.sum(list(self.vote_buffer), axis=0)  # (N_CLASSES,)
            total_votes   = np.sum(votes)
            normalized    = votes / total_votes                       # Normalize to 0-1
            best_class    = int(np.argmax(normalized))
            confidence    = float(normalized[best_class])

            if confidence >= CONFIDENCE_THRESHOLD:
                sign_label = self.labels[best_class]
                # Clear vote buffer so progress bar resets for next sign
                self.vote_buffer.clear()
                return sign_label, confidence

        except Exception as e:
            print(f"Error in MobileNetV2 inference: {e}")

        return None

    def new_session(self):
        """
        Reset for a new WebSocket session.
        No MediaPipe to recreate — just clear the vote buffer.
        """
        self.vote_buffer.clear()
        print("[+] Vote buffer cleared for new session.")

    def reset(self):
        """Legacy alias."""
        self.new_session()

    def get_all_labels(self):
        if not self._loaded:
            self.load()
        return self.labels

    def get_buffer_size(self):
        return len(self.vote_buffer)


# Singleton used by the FastAPI server
recognizer = SignRecognizer()
