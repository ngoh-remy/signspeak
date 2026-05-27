"""
SignSpeak - LSTM Model Trainer
================================
What this script does (explained for your defense):

1. LOAD DATA: We load all the .npy keypoint files created by preprocess.py.
   Each file is a (30, 1662) array - 30 frames, 1662 features per frame.

2. ENCODE LABELS: We convert word labels ("hello", "thank you") into numbers
   (0, 1, 2, ...) that the neural network can work with.

3. BUILD MODEL: We create a neural network with two types of layers:
   - LSTM (Long Short-Term Memory): These layers understand SEQUENCES of data.
     They remember what happened in earlier frames when processing later frames.
     This is perfect for sign language because a sign is a movement over time.
   - Dense layers: Standard classification layers at the end.

4. TRAIN: We show the model thousands of labeled examples so it learns to
   associate keypoint patterns with specific signs.

5. SAVE: We save the trained model to model.h5 for use by the backend server.

Why LSTM?
  A gesture is not a single image - it's a sequence of positions over time.
  LSTM networks were specifically designed for sequential data (like time series,
  speech, or video). They have "memory cells" that allow information from early
  frames to influence predictions about later frames.

Model Architecture:
  Input (30 frames × 1662 features)
       |
  LSTM(64 units) → LSTM(128 units)  [learns temporal patterns]
       |
  Dense(64, ReLU)                    [learns complex combinations]
       |
  Dropout(0.5)                       [prevents overfitting]
       |
  Dense(N_classes, Softmax)          [outputs probability for each sign]
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
import tensorflow as tf

# ─── Configuration ────────────────────────────────────────────────────────────

KEYPOINTS_PATH = os.path.join(os.path.dirname(__file__), "keypoints")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "labels.json")
MODEL_OUTPUT = os.path.join(os.path.dirname(__file__), "model.h5")
PLOTS_OUTPUT = os.path.join(os.path.dirname(__file__), "training_results")

SEQUENCE_LENGTH = 30
FEATURE_SIZE = 1662
EPOCHS = 100
BATCH_SIZE = 16
TEST_SIZE = 0.2
RANDOM_SEED = 42


def load_dataset(labels):
    """
    Load all keypoint sequences and their corresponding labels.

    Returns:
        X: numpy array of shape (n_samples, 30, 1662)
        y: numpy array of shape (n_samples,) with integer class indices
    """
    X = []
    y = []
    skipped = 0

    print("Loading keypoint data...")
    for label_idx, label in enumerate(labels):
        sign_dir = os.path.join(KEYPOINTS_PATH, label)
        if not os.path.isdir(sign_dir):
            print(f"  Warning: No keypoints found for sign '{label}'")
            continue

        npy_files = [f for f in os.listdir(sign_dir) if f.endswith(".npy")]
        for npy_file in npy_files:
            path = os.path.join(sign_dir, npy_file)
            try:
                sequence = np.load(path)
                if sequence.shape == (SEQUENCE_LENGTH, FEATURE_SIZE):
                    X.append(sequence)
                    y.append(label_idx)
                else:
                    skipped += 1
            except Exception as e:
                skipped += 1

    print(f"  Loaded {len(X)} samples, skipped {skipped}")
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def build_model(n_classes, input_shape):
    """
    Build the LSTM-based sign language recognition model.

    Architecture explanation for the defense:
    - LSTM layers process the 30-frame sequence and learn temporal dependencies
    - BatchNormalization stabilizes training and speeds convergence
    - Dropout prevents the model from memorizing training data (overfitting)
    - Final Dense layer with Softmax gives a probability distribution over classes
    """
    model = Sequential([
        # First LSTM layer - extracts low-level temporal features
        LSTM(64, return_sequences=True, activation="tanh",
             input_shape=input_shape),
        BatchNormalization(),
        Dropout(0.3),

        # Second LSTM layer - extracts higher-level temporal patterns
        LSTM(128, return_sequences=False, activation="tanh"),
        BatchNormalization(),
        Dropout(0.3),

        # Dense layers for classification
        Dense(64, activation="relu"),
        Dropout(0.5),

        # Output layer - one neuron per sign, softmax gives probabilities
        Dense(n_classes, activation="softmax"),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def plot_training_history(history, output_dir):
    """Save training accuracy and loss curves as images."""
    os.makedirs(output_dir, exist_ok=True)

    # Accuracy plot
    plt.figure(figsize=(10, 6))
    plt.plot(history.history["accuracy"], label="Training Accuracy", color="#7C3AED", linewidth=2)
    plt.plot(history.history["val_accuracy"], label="Validation Accuracy", color="#10B981", linewidth=2)
    plt.title("Model Accuracy Over Training Epochs", fontsize=14, fontweight="bold")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "accuracy.png"), dpi=150)
    plt.close()
    print(f"  Accuracy plot saved.")

    # Loss plot
    plt.figure(figsize=(10, 6))
    plt.plot(history.history["loss"], label="Training Loss", color="#EF4444", linewidth=2)
    plt.plot(history.history["val_loss"], label="Validation Loss", color="#F59E0B", linewidth=2)
    plt.title("Model Loss Over Training Epochs", fontsize=14, fontweight="bold")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "loss.png"), dpi=150)
    plt.close()
    print(f"  Loss plot saved.")


def train():
    # Load labels
    with open(LABELS_PATH, "r") as f:
        labels = json.load(f)
    n_classes = len(labels)
    print(f"Training on {n_classes} sign classes")

    # Load dataset
    X, y = load_dataset(labels)
    print(f"Dataset shape: X={X.shape}, y={y.shape}")

    if len(X) == 0:
        print("ERROR: No data found. Run preprocess.py first.")
        return

    # One-hot encode labels for categorical crossentropy loss
    y_categorical = to_categorical(y, num_classes=n_classes)

    # Train/test split - 80% training, 20% testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_categorical, test_size=TEST_SIZE, random_state=RANDOM_SEED,
        stratify=y  # Ensures each class is proportionally represented in both sets
    )
    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # Build model
    model = build_model(n_classes, input_shape=(SEQUENCE_LENGTH, FEATURE_SIZE))
    model.summary()

    # Callbacks - these monitor training and make automatic decisions:
    callbacks = [
        # Save the best model (highest validation accuracy) during training
        ModelCheckpoint(MODEL_OUTPUT, monitor="val_accuracy", save_best_only=True, verbose=1),
        # Stop training early if validation accuracy stops improving (prevents wasting time)
        EarlyStopping(monitor="val_accuracy", patience=20, restore_best_weights=True, verbose=1),
        # Reduce learning rate when training plateaus (helps escape local minima)
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=10, min_lr=1e-6, verbose=1),
    ]

    print(f"\nStarting training for up to {EPOCHS} epochs...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        verbose=1,
    )

    # Evaluate on test set
    print("\nEvaluating on test set...")
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Accuracy: {test_accuracy * 100:.2f}%")
    print(f"Test Loss: {test_loss:.4f}")

    # Save training plots
    print("\nSaving training plots...")
    plot_training_history(history, PLOTS_OUTPUT)

    print(f"\nTraining complete! Model saved to: {MODEL_OUTPUT}")
    print(f"Final test accuracy: {test_accuracy * 100:.2f}%")

    return model, history, test_accuracy


if __name__ == "__main__":
    train()
