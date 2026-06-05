"""
SignSpeak - Keypoint Data Augmentation
======================================
Why we need this:
  The model has only ~9 samples per class on average.
  Deep learning LSTM models need at least 30-50 samples per class to generalize.
  Instead of recording all new videos, we apply realistic transformations to
  existing keypoint sequences to generate additional training samples.

What augmentations we apply (all are physically plausible):
  1. Gaussian noise      — simulates slight measurement jitter in MediaPipe
  2. Horizontal mirror   — flips left/right hand (as if seen in a mirror)
  3. Time warp           — slightly speeds up or slows down parts of the sign
  4. Scale jitter        — simulates the signer being closer or farther away
  5. Frame dropout       — randomly zeroes a frame (simulates occlusion)

Each original sample → 4 augmented copies = 5× total dataset size.
Result: 447 samples → ~2235 samples (avg ~44 per class).
"""

import os
import json
import numpy as np
from tqdm import tqdm

# ─── Configuration ────────────────────────────────────────────────────────────

KEYPOINTS_PATH = os.path.join(os.path.dirname(__file__), "keypoints")
LABELS_PATH    = os.path.join(os.path.dirname(__file__), "labels.json")

SEQUENCE_LENGTH = 30
FEATURE_SIZE    = 1662

# How many augmented copies to create per original sample
AUGMENTATION_FACTOR = 4

# ─── Feature slice indices ────────────────────────────────────────────────────
# pose:       33 × 4 = 132   → indices   0 : 132
# face:      468 × 3 = 1404  → indices 132 : 1536
# left hand:  21 × 3 =   63  → indices 1536: 1599
# right hand: 21 × 3 =   63  → indices 1599: 1662

POSE_END  = 132
FACE_END  = 1536
LH_END    = 1599
RH_END    = 1662


# ─── Individual augmentation functions ───────────────────────────────────────

def aug_gaussian_noise(seq: np.ndarray, std: float = 0.005) -> np.ndarray:
    """Add small random noise to all coordinates."""
    noise = np.random.normal(0, std, seq.shape)
    return seq + noise


def aug_mirror(seq: np.ndarray) -> np.ndarray:
    """
    Flip the sign horizontally.
    For pose and face: negate x-coordinate (every 4th value for pose, every 3rd for face).
    For hands: swap left and right hand data.
    """
    aug = seq.copy()

    # --- Pose: flip x (index 0, 4, 8, ... up to POSE_END)
    for i in range(0, POSE_END, 4):
        aug[:, i] = 1.0 - aug[:, i]   # x is normalised 0-1

    # --- Face: flip x (index 0, 3, 6, ... in face slice)
    for i in range(FACE_END - POSE_END):
        if i % 3 == 0:
            col = POSE_END + i
            aug[:, col] = 1.0 - aug[:, col]

    # --- Swap left and right hand data
    lh = aug[:, FACE_END:LH_END].copy()
    rh = aug[:, LH_END:RH_END].copy()
    aug[:, FACE_END:LH_END] = rh
    aug[:, LH_END:RH_END]   = lh

    # Flip x within each hand (every 3rd value starting at 0)
    for hand_start in [FACE_END, LH_END]:
        for i in range(0, 63, 3):
            col = hand_start + i
            aug[:, col] = 1.0 - aug[:, col]

    return aug


def aug_time_warp(seq: np.ndarray, sigma: float = 0.2) -> np.ndarray:
    """
    Slightly stretch or compress segments of the sequence in time.
    Uses a smooth random warp curve via cumulative sum of random steps.
    """
    T = seq.shape[0]
    # Random displacement curve (smooth via cumsum)
    warp = np.cumsum(np.random.randn(T) * sigma)
    warp -= warp.min()
    warp /= (warp.max() + 1e-8)
    new_indices = (warp * (T - 1)).astype(int)
    new_indices = np.clip(new_indices, 0, T - 1)
    return seq[new_indices]


def aug_scale(seq: np.ndarray, scale_range: tuple = (0.85, 1.15)) -> np.ndarray:
    """Scale all spatial coordinates by a random factor (simulates distance)."""
    scale = np.random.uniform(*scale_range)
    aug = seq.copy()
    # Scale x and y coordinates but not visibility/z-depth
    # Pose: x at 0,4,8... y at 1,5,9...
    for i in range(0, POSE_END, 4):
        aug[:, i]   *= scale   # x
        aug[:, i+1] *= scale   # y
    # Face: x at 0,3,6... y at 1,4,7...
    for i in range(0, FACE_END - POSE_END, 3):
        aug[:, POSE_END + i]   *= scale
        aug[:, POSE_END + i+1] *= scale
    # Hands: x at 0,3,6... y at 1,4,7...
    for hand_start in [FACE_END, LH_END]:
        for i in range(0, 63, 3):
            aug[:, hand_start + i]   *= scale
            aug[:, hand_start + i+1] *= scale
    return aug


def aug_frame_dropout(seq: np.ndarray, drop_prob: float = 0.1) -> np.ndarray:
    """Randomly zero out a few frames to simulate occlusion."""
    aug = seq.copy()
    for t in range(seq.shape[0]):
        if np.random.random() < drop_prob:
            aug[t] = 0.0
    return aug


# ─── Augmentation pipeline ────────────────────────────────────────────────────

AUGMENTATIONS = [
    ("noise",   aug_gaussian_noise),
    ("mirror",  aug_mirror),
    ("warp",    aug_time_warp),
    ("scale",   aug_scale),
    ("dropout", aug_frame_dropout),
]


def augment_sequence(seq: np.ndarray, aug_idx: int) -> np.ndarray:
    """
    Apply a deterministic combination of augmentations based on aug_idx.
    This ensures reproducibility and varied augmentation styles.
    """
    np.random.seed(aug_idx * 42 + 7)  # reproducible per sample

    # Each augmentation index gets a slightly different combination
    combos = [
        [aug_gaussian_noise, aug_scale],
        [aug_mirror],
        [aug_time_warp, aug_gaussian_noise],
        [aug_scale, aug_frame_dropout],
        [aug_mirror, aug_gaussian_noise],
    ]
    combo = combos[aug_idx % len(combos)]
    result = seq.copy()
    for fn in combo:
        result = fn(result)
    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def augment_dataset():
    with open(LABELS_PATH) as f:
        labels = json.load(f)

    print(f"Found {len(labels)} sign classes.")
    print(f"Augmentation factor: {AUGMENTATION_FACTOR}x (each sample -> {AUGMENTATION_FACTOR} new copies)")

    total_original  = 0
    total_augmented = 0
    skipped         = 0

    for label in tqdm(labels, desc="Augmenting"):
        sign_dir = os.path.join(KEYPOINTS_PATH, label)
        if not os.path.isdir(sign_dir):
            print(f"  Warning: no keypoints for '{label}' — skipping")
            continue

        # Only process ORIGINAL files (not ones we already augmented)
        npy_files = [f for f in os.listdir(sign_dir)
                     if f.endswith(".npy") and "_aug" not in f]
        total_original += len(npy_files)

        for npy_file in npy_files:
            path = os.path.join(sign_dir, npy_file)
            try:
                seq = np.load(path)
            except Exception:
                skipped += 1
                continue

            if seq.shape != (SEQUENCE_LENGTH, FEATURE_SIZE):
                skipped += 1
                continue

            stem = os.path.splitext(npy_file)[0]

            for aug_idx in range(AUGMENTATION_FACTOR):
                out_name = f"{stem}_aug{aug_idx}.npy"
                out_path = os.path.join(sign_dir, out_name)

                # Skip if already exists (safe to rerun)
                if os.path.exists(out_path):
                    total_augmented += 1
                    continue

                aug_seq = augment_sequence(seq, aug_idx)
                np.save(out_path, aug_seq.astype(np.float32))
                total_augmented += 1

    print(f"\nAugmentation complete!")
    print(f"  Original samples : {total_original}")
    print(f"  New augmented    : {total_augmented}")
    print(f"  Total dataset    : {total_original + total_augmented}")
    print(f"  Skipped          : {skipped}")
    print(f"\nNow run: python train.py")


if __name__ == "__main__":
    augment_dataset()
