"""
SignSpeak - Sign Language Dataset Preprocessor
===============================================
What this script does (explained for your defense):

1. We read every MP4 video from the dataset (SL folder).
2. For each video frame, we use MediaPipe Holistic to detect:
   - 33 body pose landmarks (x, y, z, visibility)
   - 21 left hand landmarks (x, y, z)
   - 21 right hand landmarks (x, y, z)
   This gives us a numerical "fingerprint" of the body position in each frame.
3. We sample exactly 30 frames per video (padding or truncating as needed).
4. Each video becomes a (30, 1662) array of numbers.
5. We save these arrays as .npy files - much faster to load than re-processing videos.

Why MediaPipe?
  MediaPipe is a Google framework that runs landmark detection in real time.
  Instead of feeding raw pixel images into a neural network (which requires huge
  data and computation), we extract meaningful hand/pose coordinates first.
  This makes our model lightweight, fast, and interpretable.
"""

import os
import cv2
import numpy as np
import mediapipe as mp
import json
from tqdm import tqdm

# ─── Configuration ────────────────────────────────────────────────────────────

# Path to the sign language dataset
SL_PATH = os.path.join(os.path.dirname(__file__), "SL")

# Where preprocessed keypoints will be saved
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "keypoints")

# How many frames we sample from each video
SEQUENCE_LENGTH = 30

# The 100 most useful/common signs to train on for the demo
# (The system supports all 2000, but we train on 100 for speed and accuracy)
TOP_SIGNS = [
    "hello", "thank you", "please", "sorry", "yes", "no", "help",
    "love", "good", "bad", "name", "what", "how", "where", "who",
    "want", "need", "like", "eat", "drink", "go", "come", "stop",
    "wait", "understand", "again", "finish", "more", "less", "big",
    "small", "happy", "sad", "angry", "sick", "pain", "doctor",
    "hospital", "school", "home", "family", "mother", "father",
    "brother", "sister", "friend", "man", "woman", "child",
    "water"
]

# ─── MediaPipe Setup ──────────────────────────────────────────────────────────

mp_holistic = mp.solutions.holistic


def extract_keypoints(results):
    """
    Extract landmark coordinates from a MediaPipe Holistic result.

    Returns a flat numpy array of shape (1662,):
    - Pose: 33 landmarks × 4 values (x, y, z, visibility) = 132
    - Face: 468 landmarks × 3 values (x, y, z) = 1404  <-- set to 0 for speed
    - Left hand: 21 landmarks × 3 values = 63
    - Right hand: 21 landmarks × 3 values = 63
    Total = 132 + 1404 + 63 + 63 = 1662
    """
    # Pose landmarks (whole body skeleton)
    if results.pose_landmarks:
        pose = np.array([[lm.x, lm.y, lm.z, lm.visibility]
                         for lm in results.pose_landmarks.landmark]).flatten()
    else:
        pose = np.zeros(33 * 4)

    # Face landmarks (we include but zero them out to focus on hands/pose)
    if results.face_landmarks:
        face = np.array([[lm.x, lm.y, lm.z]
                         for lm in results.face_landmarks.landmark]).flatten()
    else:
        face = np.zeros(468 * 3)

    # Left hand landmarks
    if results.left_hand_landmarks:
        lh = np.array([[lm.x, lm.y, lm.z]
                       for lm in results.left_hand_landmarks.landmark]).flatten()
    else:
        lh = np.zeros(21 * 3)

    # Right hand landmarks
    if results.right_hand_landmarks:
        rh = np.array([[lm.x, lm.y, lm.z]
                       for lm in results.right_hand_landmarks.landmark]).flatten()
    else:
        rh = np.zeros(21 * 3)

    return np.concatenate([pose, face, lh, rh])


def process_video(video_path, holistic):
    """
    Process a single video file and extract SEQUENCE_LENGTH frames of keypoints.

    Strategy:
    - Read all frames, extract keypoints for each
    - If video has fewer than SEQUENCE_LENGTH frames, pad with zeros at the end
    - If video has more, sample evenly across the video
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR (OpenCV default) to RGB (MediaPipe expects RGB)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Run MediaPipe Holistic detection
        results = holistic.process(image)

        # Extract keypoints from this frame
        keypoints = extract_keypoints(results)
        frames.append(keypoints)

    cap.release()

    if len(frames) == 0:
        return None

    # Sample or pad to SEQUENCE_LENGTH frames
    if len(frames) >= SEQUENCE_LENGTH:
        # Sample evenly distributed frames
        indices = np.linspace(0, len(frames) - 1, SEQUENCE_LENGTH, dtype=int)
        sequence = np.array([frames[i] for i in indices])
    else:
        # Pad with zeros at the end
        sequence = np.array(frames)
        padding = np.zeros((SEQUENCE_LENGTH - len(frames), 1662))
        sequence = np.vstack([sequence, padding])

    return sequence  # Shape: (30, 1662)


def preprocess_dataset():
    """
    Main preprocessing pipeline.

    Iterates over every sign in TOP_SIGNS, processes each video,
    and saves the keypoints to disk.
    """
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # Filter to only signs that exist in the dataset
    available_signs = [s for s in TOP_SIGNS if os.path.isdir(os.path.join(SL_PATH, s))]
    print(f"Processing {len(available_signs)} signs out of {len(TOP_SIGNS)} requested.")

    # Save the labels list so the model and backend use the same ordering
    labels_path = os.path.join(os.path.dirname(__file__), "labels.json")
    with open(labels_path, "w") as f:
        json.dump(available_signs, f, indent=2)
    print(f"Labels saved to {labels_path}")

    stats = {"processed": 0, "skipped": 0, "total_videos": 0}

    with mp_holistic.Holistic(
        static_image_mode=False,
        model_complexity=2,        # Higher accuracy landmark detection (was 1)
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as holistic:

        for sign_idx, sign in enumerate(tqdm(available_signs, desc="Processing signs")):
            sign_dir = os.path.join(SL_PATH, sign)
            output_sign_dir = os.path.join(OUTPUT_PATH, sign)
            os.makedirs(output_sign_dir, exist_ok=True)

            # Get all MP4 videos for this sign
            videos = [f for f in os.listdir(sign_dir) if f.endswith(".mp4")]
            stats["total_videos"] += len(videos)

            for video_file in videos:
                video_path = os.path.join(sign_dir, video_file)
                video_name = os.path.splitext(video_file)[0]
                output_path = os.path.join(output_sign_dir, f"{video_name}.npy")

                # Skip if already processed
                if os.path.exists(output_path):
                    stats["processed"] += 1
                    continue

                sequence = process_video(video_path, holistic)

                if sequence is not None:
                    np.save(output_path, sequence)
                    stats["processed"] += 1
                else:
                    stats["skipped"] += 1
                    print(f"  Warning: Could not process {video_path}")

    print(f"\nPreprocessing complete!")
    print(f"  Processed: {stats['processed']} videos")
    print(f"  Skipped:   {stats['skipped']} videos")
    print(f"  Total:     {stats['total_videos']} videos")
    print(f"  Output:    {OUTPUT_PATH}")

    # Per-class summary — helps identify which signs need more recordings
    print("\nSamples per class (non-augmented):")
    for sign in available_signs:
        sign_dir = os.path.join(OUTPUT_PATH, sign)
        if os.path.isdir(sign_dir):
            count = len([f for f in os.listdir(sign_dir)
                         if f.endswith(".npy") and "_aug" not in f])
            bar = "|" * (count // 2)
            flag = "  [LOW] consider recording more" if count < 15 else ""
            print(f"  {sign:<20} {count:>3} {bar}{flag}")
    print("\nNext steps:")
    print("  1. python augment.py    <- multiply data 5x")
    print("  2. python train.py      <- retrain model")


if __name__ == "__main__":
    preprocess_dataset()
