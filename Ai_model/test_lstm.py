"""
SignSpeak - LSTM Real-time Camera Test
"""

import os
import cv2
import numpy as np
import pickle
import mediapipe as mp
import tensorflow as tf

# Suppress TF logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

MODEL_PATH   = os.path.join(os.path.dirname(__file__), "best_model_lstm.keras")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "label_encoder_lstm.pkl")

print("Loading model and labels...")
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(ENCODER_PATH, "rb") as f:
        label_encoder = pickle.load(f)
    labels = list(label_encoder.classes_)
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please make sure you have run train_lstm.py first!")
    exit(1)

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

sequence = []
CONFIDENCE_THRESHOLD = 0.50

print("Starting camera... Press 'q' to quit.")

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1) # Mirror
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = holistic.process(image)
        image.flags.writeable = True
        
        # Draw landmarks
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        
        # Extract features
        keypoints = extract_keypoints(results)
        sequence.append(keypoints)
        
        # Maintain a rolling window of 30 frames
        sequence = sequence[-30:]
        
        if len(sequence) == 30:
            from normalize import normalize_keypoints
            # normalize_keypoints expects shape (frames, features)
            normalized_seq = normalize_keypoints(np.array(sequence))
            
            res = model.predict(np.expand_dims(normalized_seq, axis=0), verbose=0)[0]
            best_class = int(np.argmax(res))
            confidence = float(res[best_class])
            
            if confidence >= CONFIDENCE_THRESHOLD:
                sign_label = labels[best_class]
                cv2.putText(frame, f"{sign_label} ({confidence*100:.1f}%)", (10, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            else:
                cv2.putText(frame, "Waiting...", (10, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        else:
            cv2.putText(frame, f"Buffering... {len(sequence)}/30", (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 165, 0), 2)
            
        cv2.imshow("SignSpeak LSTM Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
