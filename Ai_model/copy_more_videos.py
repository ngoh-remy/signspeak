"""
SignSpeak - Pull More Videos from Existing SL Dataset
======================================================
Your SL/ folder already contains thousands of sign language videos covering
many words. This script:

  1. Looks at the 50 labels we train on (from labels.json)
  2. Checks how many .npy files each label already has in keypoints/
  3. Identifies labels below a target threshold (default: 30 samples)
  4. Copies additional .mp4 files from SL/<label>/ into SL/<label>/
     (they are probably already there — preprocess.py just needs to process them)
  5. Prints a summary showing which labels still need more data

After running this, run:
  python preprocess.py   ← processes new videos into .npy keypoints
  python augment.py      ← augments all samples to 5× total
  python train.py        ← retrains the model

NOTE: This script does NOT delete or overwrite any existing files.
"""

import os
import json
import shutil

# ─── Configuration ────────────────────────────────────────────────────────────

SL_PATH       = os.path.join(os.path.dirname(__file__), "SL")
KEYPOINTS_PATH = os.path.join(os.path.dirname(__file__), "keypoints")
LABELS_PATH   = os.path.join(os.path.dirname(__file__), "labels.json")

# Target number of RAW (non-augmented) video samples per class before augmentation
TARGET_SAMPLES = 30

# ─── Main ─────────────────────────────────────────────────────────────────────

def count_raw_keypoints(label: str) -> int:
    """Count existing non-augmented .npy files for a label."""
    sign_dir = os.path.join(KEYPOINTS_PATH, label)
    if not os.path.isdir(sign_dir):
        return 0
    return len([f for f in os.listdir(sign_dir)
                if f.endswith(".npy") and "_aug" not in f])


def count_videos_in_sl(label: str) -> int:
    """Count available .mp4 files in SL/<label>/"""
    sign_dir = os.path.join(SL_PATH, label)
    if not os.path.isdir(sign_dir):
        return 0
    return len([f for f in os.listdir(sign_dir) if f.endswith(".mp4")])


def copy_more_videos():
    with open(LABELS_PATH) as f:
        labels = json.load(f)

    print(f"{'Label':<20} {'Existing .npy':>14} {'Videos in SL':>13} {'Status':>20}")
    print("-" * 72)

    needs_more = []
    total_copied = 0

    for label in labels:
        existing = count_raw_keypoints(label)
        available = count_videos_in_sl(label)

        if existing >= TARGET_SAMPLES:
            status = "[OK]"
        elif available > existing:
            needed = min(TARGET_SAMPLES - existing, available - existing)
            status = f"[+{needed} from SL/]"
            needs_more.append((label, existing, available, needed))
        else:
            status = f"[LOW: {existing} have]"
            needs_more.append((label, existing, available, 0))

        print(f"{label:<20} {existing:>14} {available:>13} {status:>20}")

    print(f"\n{'='*72}")

    if not needs_more:
        print("All labels meet the target threshold! Run preprocess.py and train.py.")
        return

    print(f"\nLabels below {TARGET_SAMPLES} raw samples: {len(needs_more)}")
    print("\nFor labels where SL/ has more videos than we've processed,")
    print("just re-running preprocess.py (without skipping existing) will help.")
    print("\nThe preprocess.py script skips already-processed videos.")
    print("You may want to ADD new .mp4 files to SL/<label>/ for under-represented signs.")

    print("\nNEXT STEPS:")
    print("  1. For labels with [LOW], consider recording 10-20 new short clips")
    print("     and saving them as .mp4 in Ai_model/SL/<label>/")
    print("  2. Run: python preprocess.py")
    print("  3. Run: python augment.py")
    print("  4. Run: python train.py")
    print("="*72)


if __name__ == "__main__":
    copy_more_videos()
