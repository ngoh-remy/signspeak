"""
SignSpeak - LSTM Feature Extraction (MediaPipe Holistic)
Extracts Pose, Left Hand, and Right Hand landmarks into a 258-dimensional vector.
Saves the results as X.npy and y.npy for fast LSTM training.
"""

import os
import cv2
import json
import numpy as np
import mediapipe as mp
from concurrent.futures import ProcessPoolExecutor

SL_PATH    = os.path.join(os.path.dirname(__file__), "SL")
OUTPUT_DIR = os.path.dirname(__file__)

FRAMES_PER = 30
MIN_VIDEOS = 10

def extract_keypoints(results):
    """Flatten Pose, Left Hand, and Right Hand landmarks into a single 1D array (Length: 258)"""
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

def process_single_video(item):
    sign, video_file, sl_path = item
    video_path = os.path.join(sl_path, sign, video_file)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
        
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = set(np.linspace(0, max(0, total - 1), FRAMES_PER, dtype=int))
    
    video_features = []
    frame_idx = 0
    
    mp_holistic = mp.solutions.holistic
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_idx in indices:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False                  
                results = holistic.process(image)
                
                keypoints = extract_keypoints(results)
                video_features.append(keypoints)
                
            frame_idx += 1

    cap.release()
    
    if len(video_features) == 0:
        return None
        
    # Ensure exactly FRAMES_PER frames (pad by duplicating last frame if necessary)
    while len(video_features) < FRAMES_PER:
        video_features.append(video_features[-1])
        
    # Take exactly FRAMES_PER frames
    video_features = video_features[:FRAMES_PER]
    
    return sign, np.array(video_features)

def main():
    print("=" * 60)
    print("  SignSpeak LSTM Feature Extraction (Holistic)")
    print("=" * 60)
    print()
    
    # 1. Select signs with enough videos
    sign_counts = {}
    for sign_dir in os.listdir(SL_PATH):
        full_path = os.path.join(SL_PATH, sign_dir)
        if not os.path.isdir(full_path): continue
        videos = [f for f in os.listdir(full_path) if f.endswith(".mp4")]
        if len(videos) >= MIN_VIDEOS:
            sign_counts[sign_dir] = len(videos)
            
    sign_counts = dict(sorted(sign_counts.items(), key=lambda x: x[1], reverse=True))
    SELECTED_SIGNS = list(sign_counts.keys())
    
    print(f"Found {len(SELECTED_SIGNS)} signs with {MIN_VIDEOS}+ videos.")
    print(f"Total videos to process: {sum(sign_counts.values())}")
    
    # Save the labels file
    labels_path = os.path.join(OUTPUT_DIR, "labels_lstm.json")
    with open(labels_path, "w") as f:
        json.dump(SELECTED_SIGNS, f, indent=2)
        
    # 2. Build task list
    tasks = []
    for sign in SELECTED_SIGNS:
        sign_dir = os.path.join(SL_PATH, sign)
        videos = [f for f in os.listdir(sign_dir) if f.endswith(".mp4")]
        for video_file in videos:
            tasks.append((sign, video_file, SL_PATH))
            
    workers = min(6, os.cpu_count() or 1)
    print(f"\nExtracting features using {workers} CPU workers... This will take a few minutes.")
    
    X_data = []
    y_data = []
    skipped = 0
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        for i, res in enumerate(executor.map(process_single_video, tasks)):
            if res is None:
                skipped += 1
            else:
                sign, features = res
                X_data.append(features)
                y_data.append(sign)
                
            if (i+1) % 50 == 0:
                print(f"  Processed {i+1}/{len(tasks)} videos...")
                
    X = np.array(X_data)
    y = np.array(y_data)
    
    print(f"\nExtraction complete!")
    print(f"X shape: {X.shape}  -> (Videos, Frames, Features)")
    print(f"y shape: {y.shape}")
    print(f"Skipped videos: {skipped}")
    
    # Save arrays
    print("\nSaving numpy arrays...")
    np.save(os.path.join(OUTPUT_DIR, "X.npy"), X)
    np.save(os.path.join(OUTPUT_DIR, "y.npy"), y)
    print("Saved X.npy and y.npy to Ai_model directory.")
    print("You can now run train_lstm.py instantly!")

if __name__ == "__main__":
    main()
