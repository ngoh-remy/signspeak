"""
SignSpeak - LSTM Model Trainer (v2 - Improved Architecture)
============================================================
What this script does (explained for your defense):

1. LOAD DATA: We load all the .npy keypoint files created by preprocess.py
   and augmented by augment.py. Each file is a (30, 1662) array -
   30 frames, 1662 features per frame.

2. ENCODE LABELS: We convert word labels ("hello", "thank you") into numbers
   (0, 1, 2, ...) that the neural network can work with.

3. BUILD MODEL: We create a neural network with:
   - LSTM (Long Short-Term Memory): Understands SEQUENCES of data over time.
     Perfect for sign language because a sign is a movement over time.
   - BatchNormalization: Stabilises training, speeds convergence.
   - Dropout: Prevents the model from memorizing instead of learning.
   - Dense layers: Standard classification layers at the end.

4. TRAIN: We show the model thousands of labeled examples and use class
   weighting to compensate for any imbalance between sign classes.

5. SAVE: We save the best model to model.h5 for use by the backend server.

Why LSTM?
  A gesture is not a single image - it's a sequence of positions over time.
  LSTM networks were specifically designed for sequential data (like time
  series, speech, or video). They have "memory cells" that allow information
  from early frames to influence predictions about later frames.

Model Architecture (v2 - deeper and wider):
  Input (30 frames x 1662 features)
       |
  LSTM(128) -> LSTM(256) -> LSTM(128)  [learns temporal patterns at 3 scales]
       |
  Dense(128, ReLU) -> Dropout(0.3)     [learns class-discriminating features]
       |
  Dense(N_classes, Softmax)            [outputs probability for each sign]

Changes from v1:
  - Larger LSTM units (64->128, 128->256, added 3rd LSTM layer)
  - Class weighting to handle imbalanced sample counts per sign
  - More epochs (200) with longer patience (30)
  - Confusion matrix saved to training_results/
  - Per-class accuracy report at the end
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
import tensorflow as tf

# ─── Configuration ────────────────────────────────────────────────────────────

KEYPOINTS_PATH = os.path.join(os.path.dirname(__file__), "keypoints")
LABELS_PATH    = os.path.join(os.path.dirname(__file__), "labels.json")
MODEL_OUTPUT   = os.path.join(os.path.dirname(__file__), "model.h5")
PLOTS_OUTPUT   = os.path.join(os.path.dirname(__file__), "training_results")

SEQUENCE_LENGTH = 30
FEATURE_SIZE    = 1662
EPOCHS          = 200
BATCH_SIZE      = 32
TEST_SIZE       = 0.2
RANDOM_SEED     = 42


def load_dataset(labels):
    """
    Load all keypoint sequences and their corresponding labels.
    Includes both original and augmented samples.

    Returns:
        X: numpy array of shape (n_samples, 30, 1662)
        y: numpy array of shape (n_samples,) with integer class indices
    """
    X = []
    y = []
    skipped = 0

    print("Loading keypoint data...")
    class_counts = {}

    for label_idx, label in enumerate(labels):
        sign_dir = os.path.join(KEYPOINTS_PATH, label)
        if not os.path.isdir(sign_dir):
            print(f"  Warning: No keypoints found for sign '{label}'")
            class_counts[label] = 0
            continue

        npy_files = [f for f in os.listdir(sign_dir) if f.endswith(".npy")]
        count = 0
        for npy_file in npy_files:
            path = os.path.join(sign_dir, npy_file)
            try:
                sequence = np.load(path)
                if sequence.shape == (SEQUENCE_LENGTH, FEATURE_SIZE):
                    X.append(sequence)
                    y.append(label_idx)
                    count += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1
        class_counts[label] = count

    print(f"  Total samples: {len(X)}, skipped: {skipped}")
    print(f"\n  Samples per class:")
    for label, cnt in class_counts.items():
        bar = "|" * (cnt // 5) + f"  ({cnt})"
        status = "[LOW]" if cnt < 20 else "[OK]"
        print(f"    {label:<20} {bar} {status}")

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int32)


def build_model(n_classes, input_shape):
    """
    Build the improved LSTM-based sign language recognition model.

    v2 changes:
    - 3 LSTM layers instead of 2 (better temporal feature hierarchy)
    - Larger units (128 -> 256 -> 128) for more representational capacity
    - Reduced dropout to 0.3 throughout (was 0.5 in the dense layer)
    - Larger Dense head (128 instead of 64)
    """
    model = Sequential([
        # First LSTM — extracts short-term temporal patterns
        LSTM(128, return_sequences=True, activation="tanh",
             input_shape=input_shape),
        BatchNormalization(),
        Dropout(0.3),

        # Second LSTM — extracts mid-level movement patterns
        LSTM(256, return_sequences=True, activation="tanh"),
        BatchNormalization(),
        Dropout(0.3),

        # Third LSTM — extracts high-level sign-level representations
        LSTM(128, return_sequences=False, activation="tanh"),
        BatchNormalization(),
        Dropout(0.3),

        # Dense classification head
        Dense(128, activation="relu"),
        Dropout(0.3),

        # Output — one neuron per sign class
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
    plt.plot(history.history["accuracy"],
             label="Training Accuracy", color="#7C3AED", linewidth=2)
    plt.plot(history.history["val_accuracy"],
             label="Validation Accuracy", color="#10B981", linewidth=2)
    plt.title("Model Accuracy Over Training Epochs", fontsize=14, fontweight="bold")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "accuracy.png"), dpi=150)
    plt.close()
    print("  Accuracy plot saved.")

    # Loss plot
    plt.figure(figsize=(10, 6))
    plt.plot(history.history["loss"],
             label="Training Loss", color="#EF4444", linewidth=2)
    plt.plot(history.history["val_loss"],
             label="Validation Loss", color="#F59E0B", linewidth=2)
    plt.title("Model Loss Over Training Epochs", fontsize=14, fontweight="bold")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "loss.png"), dpi=150)
    plt.close()
    print("  Loss plot saved.")


def plot_confusion_matrix(y_true, y_pred, labels, output_dir):
    """Save a confusion matrix heatmap to training_results/."""
    os.makedirs(output_dir, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred)
    n = len(labels)

    fig_size = max(12, n // 2)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    fig.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(n),
        yticks=np.arange(n),
        xticklabels=labels,
        yticklabels=labels,
        title="Confusion Matrix",
        ylabel="True Label",
        xlabel="Predicted Label",
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=7)
    plt.setp(ax.get_yticklabels(), fontsize=7)

    thresh = cm.max() / 2.0
    for i in range(n):
        for j in range(n):
            ax.text(j, i, str(cm[i, j]),
                    ha="center", va="center", fontsize=6,
                    color="white" if cm[i, j] > thresh else "black")

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "confusion_matrix.png"), dpi=120)
    plt.close()
    print("  Confusion matrix saved.")


def train():
    # Load labels
    with open(LABELS_PATH, "r") as f:
        labels = json.load(f)
    n_classes = len(labels)
    print(f"\nTraining on {n_classes} sign classes")
    print("=" * 50)

    # Load dataset (original + augmented)
    X, y = load_dataset(labels)
    print(f"\nDataset shape: X={X.shape}, y={y.shape}")

    if len(X) == 0:
        print("ERROR: No data found. Run preprocess.py and augment.py first.")
        return

    if len(X) < 50:
        print("WARNING: Very few samples. Run augment.py to expand the dataset.")

    # One-hot encode labels
    y_categorical = to_categorical(y, num_classes=n_classes)

    # Train/test split — 80% training, 20% testing, stratified by class
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_categorical,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=y   # ensures each class is proportionally represented
    )
    print(f"\nTrain samples: {len(X_train)}, Test samples: {len(X_test)}")

    # ── Class weighting ───────────────────────────────────────────────────────
    # This tells the model to pay more attention to underrepresented classes.
    # Signs with fewer samples get a higher weight in the loss function.
    class_weights_array = compute_class_weight(
        class_weight="balanced",
        classes=np.arange(n_classes),
        y=y
    )
    class_weight_dict = {i: w for i, w in enumerate(class_weights_array)}
    print(f"\nClass weights computed (range: "
          f"{min(class_weights_array):.2f} – {max(class_weights_array):.2f})")

    # Build model
    model = build_model(n_classes, input_shape=(SEQUENCE_LENGTH, FEATURE_SIZE))
    model.summary()

    # Callbacks
    callbacks = [
        # Save the best model (highest val accuracy)
        ModelCheckpoint(MODEL_OUTPUT,
                        monitor="val_accuracy",
                        save_best_only=True,
                        verbose=1),
        # Stop early if no improvement for 30 consecutive epochs
        EarlyStopping(monitor="val_accuracy",
                      patience=30,
                      restore_best_weights=True,
                      verbose=1),
        # Halve learning rate when val_loss stalls for 15 epochs
        ReduceLROnPlateau(monitor="val_loss",
                          factor=0.5,
                          patience=15,
                          min_lr=1e-7,
                          verbose=1),
    ]

    print(f"\nStarting training for up to {EPOCHS} epochs...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weight_dict,   # ← KEY improvement
        callbacks=callbacks,
        verbose=1,
    )

    # ── Evaluate ──────────────────────────────────────────────────────────────
    print("\nEvaluating on test set...")
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest Accuracy : {test_accuracy * 100:.2f}%")
    print(f"Test Loss     : {test_loss:.4f}")

    # Per-class report
    y_pred_probs = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)
    y_true = np.argmax(y_test, axis=1)

    print("\nPer-class classification report:")
    print(classification_report(y_true, y_pred, target_names=labels, zero_division=0))

    # Save training plots + confusion matrix
    print("\nSaving training plots...")
    plot_training_history(history, PLOTS_OUTPUT)
    plot_confusion_matrix(y_true, y_pred, labels, PLOTS_OUTPUT)

    print(f"\n{'='*50}")
    print(f"Training complete!")
    print(f"  Model saved to : {MODEL_OUTPUT}")
    print(f"  Plots saved to : {PLOTS_OUTPUT}")
    print(f"  Test accuracy  : {test_accuracy * 100:.2f}%")

    if test_accuracy < 0.6:
        print("\n  [!!] Accuracy still low. Consider:")
        print("     - Running augment.py if not done yet")
        print("     - Adding more raw videos to SL/<label>/")
        print("     - Running preprocess.py on new videos")
    elif test_accuracy < 0.8:
        print("\n  [^] Good progress! For higher accuracy:")
        print("     - Add more raw videos (record new clips)")
        print("     - Run preprocess.py + augment.py again")
    else:
        print("\n  [**] Great accuracy! The model is ready for deployment.")

    return model, history, test_accuracy


if __name__ == "__main__":
    train()
