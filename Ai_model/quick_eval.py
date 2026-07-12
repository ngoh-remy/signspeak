import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
import pickle

OUTPUT_DIR = os.path.dirname(__file__)

def main():
    X = np.load(os.path.join(OUTPUT_DIR, "X.npy"))
    y_labels = np.load(os.path.join(OUTPUT_DIR, "y.npy"))
    
    from collections import Counter
    label_counts = Counter(y_labels)
    top_20_classes = [label for label, count in label_counts.most_common(20)]
    
    indices = [i for i, label in enumerate(y_labels) if label in top_20_classes]
    X_filtered = X[indices]
    y_filtered = y_labels[indices]
    
    with open(os.path.join(OUTPUT_DIR, "label_encoder_lstm.pkl"), "rb") as f:
        encoder = pickle.load(f)
        
    y = encoder.transform(y_filtered)
    
    from normalize import normalize_keypoints
    for i in range(len(X_filtered)):
        X_filtered[i] = normalize_keypoints(X_filtered[i])
        
    X_train, X_test, y_train, y_test = train_test_split(X_filtered, y, test_size=0.2, random_state=42, stratify=y)
    
    model_path = os.path.join(OUTPUT_DIR, "best_model_lstm.keras")
    model = tf.keras.models.load_model(model_path, compile=False)
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"ACTUAL VALIDATION ACCURACY: {acc * 100:.2f}%")

if __name__ == "__main__":
    main()
