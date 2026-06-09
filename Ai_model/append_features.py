import os
import cv2
import glob
import numpy as np
import mediapipe as mp
from concurrent.futures import ProcessPoolExecutor

SL_PATH    = os.path.join(os.path.dirname(__file__), "SL")
OUTPUT_DIR = os.path.dirname(__file__)
FRAMES_PER = 30

def extract_keypoints(results):
    """Flatten Pose, Left Hand, and Right Hand landmarks into a single 1D array (Length: 258)"""
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, lh, rh])

def process_single_video(video_path):
    # Extract sign name from path: SL/<sign>/personal_xxx.mp4
    sign = os.path.basename(os.path.dirname(video_path))
    
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
    
    return sign, np.array(video_features), video_path

def main():
    print("=" * 60)
    print("  SignSpeak Personal Feature Updater")
    print("=" * 60)
    
    # 1. Find all personal videos
    search_pattern = os.path.join(SL_PATH, "*", "personal_*.mp4")
    personal_videos = glob.glob(search_pattern)
    
    if not personal_videos:
        print("No personal videos found! Did you record any using record_custom_data.py?")
        return
        
    print(f"Found {len(personal_videos)} personal videos to process.")
    
    # 2. Extract features
    workers = min(6, os.cpu_count() or 1)
    print(f"\nExtracting features using {workers} CPU workers...")
    
    new_X = []
    new_y = []
    successful_files = []
    
    print("Extracting features sequentially to avoid deadlocks...")
    for i, path in enumerate(personal_videos):
        res = process_single_video(path)
        if res is not None:
            sign, features, p = res
            new_X.append(features)
            new_y.append(sign)
            successful_files.append(p)
            
        if (i+1) % 10 == 0:
            print(f"  Processed {i+1}/{len(personal_videos)} videos...", flush=True)
                
    if not new_X:
        print("Failed to extract features from any video.")
        return
        
    new_X = np.array(new_X)
    new_y = np.array(new_y)
    
    print(f"\nExtraction complete! Extracted {len(new_X)} sequences.")
    
    # 3. Load existing dataset
    x_path = os.path.join(OUTPUT_DIR, "X.npy")
    y_path = os.path.join(OUTPUT_DIR, "y.npy")
    
    try:
        X = np.load(x_path)
        y = np.load(y_path)
        print(f"\nLoaded existing dataset:")
        print(f"X shape: {X.shape}")
        print(f"y shape: {y.shape}")
    except FileNotFoundError:
        print("Error: Could not find existing X.npy or y.npy. Creating new dataset.")
        X = np.empty((0, FRAMES_PER, 258))
        y = np.empty((0,))
        
    # 4. Append and Save
    combined_X = np.concatenate((X, new_X), axis=0)
    combined_y = np.concatenate((y, new_y), axis=0)
    
    print(f"\nSaving updated dataset...")
    print(f"New X shape: {combined_X.shape}")
    print(f"New y shape: {combined_y.shape}")
    
    np.save(x_path, combined_X)
    np.save(y_path, combined_y)
    
    # 5. Rename files so they aren't processed again next time
    for path in successful_files:
        dir_name = os.path.dirname(path)
        base_name = os.path.basename(path)
        new_name = base_name.replace("personal_", "processed_")
        os.rename(path, os.path.join(dir_name, new_name))
        
    print("\n✅ Dataset successfully updated!")
    print("All processed videos have been renamed to 'processed_*.mp4' so they won't be processed twice.")
    print("You can now run train_lstm.py")

if __name__ == "__main__":
    main()
