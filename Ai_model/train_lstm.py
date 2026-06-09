"""
SignSpeak - LSTM Training Script
Trains a sequence model using the extracted MediaPipe Holistic features.
"""

import os
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Bidirectional
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

OUTPUT_DIR = os.path.dirname(__file__)
MODEL_OUTPUT = os.path.join(OUTPUT_DIR, "best_model_lstm.keras")
ENCODER_OUTPUT = os.path.join(OUTPUT_DIR, "label_encoder_lstm.pkl")

def main():
    print("=" * 60)
    print("  SignSpeak LSTM Sequence Trainer")
    print("=" * 60)
    print()

    # 1. Load data
    print("Loading extracted features from X.npy and y.npy...")
    try:
        X = np.load(os.path.join(OUTPUT_DIR, "X.npy"))
        y_labels = np.load(os.path.join(OUTPUT_DIR, "y.npy"))
    except Exception as e:
        print("Error loading data. Did you run extract_features.py first?")
        return

    print(f"Loaded X shape: {X.shape}")
    print(f"Loaded y shape: {y_labels.shape}")
    
    # 2. Filter top 20 classes
    from collections import Counter
    label_counts = Counter(y_labels)
    top_20_classes = [label for label, count in label_counts.most_common(20)]
    print(f"\nFiltering to top 20 classes out of {len(label_counts)}...")
    
    indices = [i for i, label in enumerate(y_labels) if label in top_20_classes]
    X_filtered = X[indices]
    y_filtered = y_labels[indices]
    
    print(f"Filtered X shape: {X_filtered.shape}")
    print(f"Filtered y shape: {y_filtered.shape}")

    # 3. Encode labels
    encoder = LabelEncoder()
    y = encoder.fit_transform(y_filtered)
    n_classes = len(encoder.classes_)
    print(f"Classes: {n_classes}")

    with open(ENCODER_OUTPUT, "wb") as f:
        pickle.dump(encoder, f)

    # 4. Normalize spatial coordinates (zero-center around nose)
    print("Normalizing spatial coordinates...")
    from normalize import normalize_keypoints
    for i in range(len(X_filtered)):
        X_filtered[i] = normalize_keypoints(X_filtered[i])

    # 5. Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(X_filtered, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_test)}")

    # 6. Build Bidirectional LSTM Model
    model = Sequential([
        Bidirectional(LSTM(64, return_sequences=True, activation='tanh'), input_shape=(X_filtered.shape[1], X_filtered.shape[2])),
        Dropout(0.2),
        Bidirectional(LSTM(128, return_sequences=False, activation='tanh')),
        Dropout(0.2),
        Dense(64, activation='relu'),
        Dense(n_classes, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    # 5. Train
    callbacks = [
        ModelCheckpoint(MODEL_OUTPUT, monitor="val_accuracy", save_best_only=True, mode="max", verbose=1),
        EarlyStopping(monitor="val_accuracy", patience=20, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=10, min_lr=1e-6, verbose=1)
    ]

    print("\nStarting Training...")
    model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=200,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )

    print("\nEvaluating best model...")
    best_model = tf.keras.models.load_model(MODEL_OUTPUT)
    loss, acc = best_model.evaluate(X_test, y_test, verbose=0)
    print(f"Final Validation Accuracy: {acc * 100:.2f}%")

    y_pred = np.argmax(best_model.predict(X_test, verbose=0), axis=1)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=encoder.classes_, zero_division=0))
    print("\nTraining Complete! You can now test it with test_lstm.py.")

if __name__ == "__main__":
    main()
