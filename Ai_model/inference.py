import os
import cv2
import pickle
import numpy as np
from typing import Optional, Tuple
import mediapipe as mp

# ─── Configuration ────────────────────────────────────────────────────────────

MODEL_PATH   = os.path.join(os.path.dirname(__file__), "best_model_lstm.keras")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder_lstm.pkl")

SEQ_LENGTH = 30
CONFIDENCE_THRESHOLD = 0.50

SIMULATION_MODE = False
SIMULATION_REASON = ""

try:
    import tensorflow as tf
except ImportError:
    SIMULATION_MODE = True
    SIMULATION_REASON = "tensorflow not installed"

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

class SignRecognizer:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.labels = []
        self.sequence = []
        self._loaded = False
        self.holistic = None

    def load(self):
        if self._loaded:
            return

        global SIMULATION_MODE, SIMULATION_REASON

        if SIMULATION_MODE:
            print(f"[* WARNING *] SignSpeak starting in SIMULATION MODE: {SIMULATION_REASON}")
            self.labels = ["hello", "thank you", "please", "yes", "no", "help"]
            self._loaded = True
            return

        if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
            SIMULATION_MODE = True
            SIMULATION_REASON = "Model or encoder not found"
            self.labels = ["hello", "thank you", "yes", "no"]
            self._loaded = True
            return

        try:
            self.model = tf.keras.models.load_model(MODEL_PATH)
            with open(ENCODER_PATH, "rb") as f:
                self.label_encoder = pickle.load(f)
            self.labels = list(self.label_encoder.classes_)
            
            self.holistic = mp.solutions.holistic.Holistic(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self._loaded = True
            print(f"[+] LSTM model loaded with {len(self.labels)} classes.")
        except Exception as e:
            print(f"Error loading model: {e}")
            SIMULATION_MODE = True
            SIMULATION_REASON = str(e)
            self._loaded = True

    def process_keypoints(self, keypoints: list) -> Optional[Tuple[str, float]]:
        if not self._loaded:
            self.load()

        if SIMULATION_MODE:
            self.sequence.append(1)
            if len(self.sequence) >= SEQ_LENGTH:
                self.sequence = []
                import random
                return random.choice(self.labels), random.uniform(0.75, 0.99)
            return None

        # keypoints is expected to be a 258-length flat list of floats from the frontend
        if len(keypoints) != 258:
            print(f"Warning: Expected 258 keypoints, got {len(keypoints)}")
            return None

        self.sequence.append(np.array(keypoints))
        self.sequence = self.sequence[-SEQ_LENGTH:]
        
        if len(self.sequence) == SEQ_LENGTH:
            try:
                from normalize import normalize_keypoints
                normalized_seq = normalize_keypoints(np.array(self.sequence))
                res = self.model.predict(np.expand_dims(normalized_seq, axis=0), verbose=0)[0]
                best_class = int(np.argmax(res))
                confidence = float(res[best_class])
                
                if confidence >= CONFIDENCE_THRESHOLD:
                    self.sequence = [] # Clear buffer
                    return self.labels[best_class], confidence
            except Exception as e:
                print(f"Prediction error: {e}")
                
        return None

    def process_frame(self, frame_bytes: bytes) -> Optional[Tuple[str, float]]:
        if not self._loaded:
            self.load()

        if SIMULATION_MODE:
            self.sequence.append(1)
            if len(self.sequence) >= SEQ_LENGTH:
                self.sequence = []
                import random
                return random.choice(self.labels), random.uniform(0.75, 0.99)
            return None

        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return None

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.holistic.process(image)
        
        keypoints = extract_keypoints(results)
        self.sequence.append(keypoints)
        self.sequence = self.sequence[-SEQ_LENGTH:]
        
        if len(self.sequence) == SEQ_LENGTH:
            try:
                from normalize import normalize_keypoints
                normalized_seq = normalize_keypoints(np.array(self.sequence))
                res = self.model.predict(np.expand_dims(normalized_seq, axis=0), verbose=0)[0]
                best_class = int(np.argmax(res))
                confidence = float(res[best_class])
                
                if confidence >= CONFIDENCE_THRESHOLD:
                    self.sequence = [] # Clear buffer
                    return self.labels[best_class], confidence
            except Exception as e:
                print(f"Prediction error: {e}")
                
        return None

    def new_session(self):
        self.sequence = []
        
    def reset(self):
        self.new_session()

    def get_all_labels(self):
        if not self._loaded:
            self.load()
        return self.labels

    def get_buffer_size(self):
        return len(self.sequence)

recognizer = SignRecognizer()
