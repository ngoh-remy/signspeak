import os
import cv2
import pickle
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from concurrent.futures import ProcessPoolExecutor

SL_PATH = os.path.join(os.path.dirname(__file__), "SL")
IMG_SIZE = 64
FRAMES_PER = 30
MIN_VIDEOS = 10

def extract_frames(video_path, n_frames=FRAMES_PER, img_size=IMG_SIZE):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < n_frames:
        frames_raw = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (img_size, img_size))
            frames_raw.append(gray)
        cap.release()
        if len(frames_raw) == 0:
            return None
        while len(frames_raw) < n_frames:
            frames_raw.append(frames_raw[-1])
        frames_np = np.array(frames_raw[:n_frames], dtype=np.float32) / 255.0
    else:
        indices = set(np.linspace(0, total - 1, n_frames, dtype=int))
        frames_raw = []
        frame_idx = 0
        while len(frames_raw) < n_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx in indices:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (img_size, img_size))
                frames_raw.append(gray)
            frame_idx += 1
        cap.release()
        if len(frames_raw) < n_frames:
            if len(frames_raw) == 0:
                return None
            while len(frames_raw) < n_frames:
                frames_raw.append(frames_raw[-1])
        frames_np = np.array(frames_raw[:n_frames], dtype=np.float32) / 255.0
    return frames_np.reshape(n_frames, img_size, img_size, 1)

def process_single_video(item):
    sign, video_file, sl_path = item
    video_path = os.path.join(sl_path, sign, video_file)
    frames = extract_frames(video_path, n_frames=FRAMES_PER, img_size=IMG_SIZE)
    if frames is None:
        return None
    return sign, frames

def main():
    print("Scanning dataset...")
    sign_counts = {}
    for sign_dir in os.listdir(SL_PATH):
        full_path = os.path.join(SL_PATH, sign_dir)
        if not os.path.isdir(full_path):
            continue
        videos = [f for f in os.listdir(full_path) if f.endswith(".mp4")]
        if len(videos) >= MIN_VIDEOS:
            sign_counts[sign_dir] = len(videos)

    sign_counts = dict(sorted(sign_counts.items(), key=lambda x: x[1], reverse=True))
    SELECTED_SIGNS = list(sign_counts.keys())
    print(f"Found {len(SELECTED_SIGNS)} signs.")

    tasks = []
    for sign in SELECTED_SIGNS:
        sign_dir = os.path.join(SL_PATH, sign)
        videos = [f for f in os.listdir(sign_dir) if f.endswith(".mp4")]
        for video_file in videos:
            tasks.append((sign, video_file, SL_PATH))

    workers = max(1, os.cpu_count() - 2)
    print(f"Processing {len(tasks)} videos with {workers} workers...")
    
    X_flat = []
    y_flat = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(process_single_video, tasks))

    for res in results:
        if res is None:
            continue
        sign, frames = res
        for frame in frames:
            X_flat.append(frame)
            y_flat.append(sign)

    X = np.array(X_flat, dtype=np.float32)
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_flat)

    print("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded
    )

    X_test_rgb = np.repeat(X_test, 3, axis=-1)

    print("Loading model...")
    # Load H5 model first, fallback to Keras if needed
    model_path = os.path.join(os.path.dirname(__file__), "best_model.h5")
    if not os.path.exists(model_path):
        model_path = os.path.join(os.path.dirname(__file__), "best_model.keras")
    
    model = tf.keras.models.load_model(model_path, compile=False)

    print("Running evaluation...")
    y_pred = np.argmax(model.predict(X_test_rgb, verbose=0), axis=1)

    report = classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0,
        output_dict=True
    )

    report_text = classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    )

    # Save to a text file
    out_path = os.path.join(os.path.dirname(__file__), "classification_report.txt")
    with open(out_path, "w") as f:
        f.write(report_text)
    print(f"Saved full report to {out_path}")

    # Print summary metrics
    print("\n=== Summary Metrics ===")
    print(f"Accuracy: {report['accuracy']*100:.2f}%")
    print(f"Macro Avg Precision: {report['macro avg']['precision']*100:.2f}%")
    print(f"Macro Avg Recall: {report['macro avg']['recall']*100:.2f}%")
    print(f"Macro Avg F1-score: {report['macro avg']['f1-score']*100:.2f}%")
    print(f"Weighted Avg F1-score: {report['weighted avg']['f1-score']*100:.2f}%")

if __name__ == "__main__":
    main()
