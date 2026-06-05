"""
SignSpeak - Sign Language Video Recorder
=========================================
Records short webcam clips for sign language training data.

How to use:
  1. Run: python record_signs.py
  2. A window opens showing your webcam feed
  3. Press SPACE to start recording a 3-second clip
  4. Perform the sign shown on screen
  5. The clip is auto-saved as .mp4 in SL/<sign>/
  6. Press 'n' to skip to the next sign
  7. Press 'q' to quit

It automatically targets the signs that need more data.
"""

import os
import cv2
import time
import json

# ---- Configuration ----

SL_PATH       = os.path.join(os.path.dirname(__file__), "SL")
LABELS_PATH   = os.path.join(os.path.dirname(__file__), "labels.json")
KEYPOINTS_PATH = os.path.join(os.path.dirname(__file__), "keypoints")

CLIP_DURATION  = 3       # seconds per clip
FPS            = 30      # frames per second
TARGET_SAMPLES = 20      # target raw samples per class

# Signs that need more data (from training results)
PRIORITY_SIGNS = [
    ("stop",   15),   # F1=0.67, only 5 videos  -> need 15 more
    ("school", 10),   # F1=0.71, only 9 videos  -> need 10 more
    ("friend", 10),   # F1=0.80, only 7 videos  -> need 10 more
    ("come",    9),   # F1=0.83, only 6 videos  -> need 9 more
    ("no",      5),   # F1=0.82, 11 videos      -> need 5 more
    ("yes",     3),   # F1=0.83, 12 videos       -> need 3 more
]


def count_existing_videos(sign):
    """Count how many .mp4 files already exist for a sign."""
    sign_dir = os.path.join(SL_PATH, sign)
    if not os.path.isdir(sign_dir):
        return 0
    return len([f for f in os.listdir(sign_dir) if f.endswith(".mp4")])


def get_next_filename(sign):
    """Generate the next available filename for a sign."""
    sign_dir = os.path.join(SL_PATH, sign)
    os.makedirs(sign_dir, exist_ok=True)
    existing = [f for f in os.listdir(sign_dir) if f.endswith(".mp4")]
    idx = len(existing) + 1
    return os.path.join(sign_dir, f"{sign}_recorded_{idx:03d}.mp4")


def draw_text(frame, text, pos, font_scale=0.8, color=(255, 255, 255),
              thickness=2, bg_color=(0, 0, 0)):
    """Draw text with a background rectangle for readability."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    x, y = pos
    # Background rectangle
    cv2.rectangle(frame,
                  (x - 5, y - text_size[1] - 10),
                  (x + text_size[0] + 5, y + 5),
                  bg_color, -1)
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)


def record_signs():
    print("=" * 60)
    print("  SignSpeak - Sign Language Video Recorder")
    print("=" * 60)
    print()
    print("Controls:")
    print("  SPACE  = Start recording a 3-second clip")
    print("  N      = Skip to next sign")
    print("  Q      = Quit")
    print()

    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        print("Make sure no other app is using the camera.")
        return

    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    total_recorded = 0

    for sign, needed in PRIORITY_SIGNS:
        existing = count_existing_videos(sign)
        recorded_this_sign = 0

        print(f"\n--- Sign: '{sign}' ---")
        print(f"    Existing: {existing} videos")
        print(f"    Target:   {needed} more clips")

        while recorded_this_sign < needed:
            # Show live preview
            ret, frame = cap.read()
            if not ret:
                continue

            # Flip for mirror effect (more natural)
            frame = cv2.flip(frame, 1)

            # Draw UI overlay
            remaining = needed - recorded_this_sign
            draw_text(frame,
                      f"Sign: {sign.upper()}",
                      (20, 40), font_scale=1.2,
                      color=(0, 255, 128), bg_color=(30, 30, 30))
            draw_text(frame,
                      f"Recorded: {recorded_this_sign}/{needed}  |  Remaining: {remaining}",
                      (20, 80), font_scale=0.7,
                      color=(200, 200, 200))
            draw_text(frame,
                      "SPACE=Record | N=Next sign | Q=Quit",
                      (20, 460), font_scale=0.6,
                      color=(180, 180, 180))

            cv2.imshow("SignSpeak Recorder", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print(f"\nQuitting. Total clips recorded: {total_recorded}")
                cap.release()
                cv2.destroyAllWindows()
                _print_next_steps(total_recorded)
                return

            elif key == ord('n'):
                print(f"  Skipping '{sign}' ({recorded_this_sign}/{needed} recorded)")
                break

            elif key == ord(' '):
                # === COUNTDOWN ===
                for countdown in [3, 2, 1]:
                    ret, frame = cap.read()
                    if ret:
                        frame = cv2.flip(frame, 1)
                        draw_text(frame,
                                  f"Get ready: {countdown}",
                                  (180, 250), font_scale=2.0,
                                  color=(0, 200, 255), bg_color=(30, 30, 30))
                        draw_text(frame,
                                  f"Sign: {sign.upper()}",
                                  (20, 40), font_scale=1.2,
                                  color=(0, 255, 128), bg_color=(30, 30, 30))
                        cv2.imshow("SignSpeak Recorder", frame)
                    cv2.waitKey(1000)

                # === RECORDING ===
                out_path = get_next_filename(sign)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(out_path, fourcc, FPS, (640, 480))

                start_time = time.time()
                frame_count = 0

                while time.time() - start_time < CLIP_DURATION:
                    ret, frame = cap.read()
                    if not ret:
                        continue

                    frame = cv2.flip(frame, 1)
                    out.write(cv2.flip(frame, 1))  # Save un-mirrored
                    frame_count += 1

                    # Recording indicator
                    elapsed = time.time() - start_time
                    progress = int((elapsed / CLIP_DURATION) * 100)

                    # Red recording dot
                    cv2.circle(frame, (30, 40), 12, (0, 0, 255), -1)
                    draw_text(frame,
                              f"  RECORDING '{sign.upper()}'  {progress}%",
                              (50, 50), font_scale=0.9,
                              color=(0, 0, 255))

                    # Progress bar
                    bar_width = int(600 * elapsed / CLIP_DURATION)
                    cv2.rectangle(frame, (20, 465), (620, 475), (60, 60, 60), -1)
                    cv2.rectangle(frame, (20, 465), (20 + bar_width, 475),
                                  (0, 0, 255), -1)

                    cv2.imshow("SignSpeak Recorder", frame)
                    cv2.waitKey(1)

                out.release()
                recorded_this_sign += 1
                total_recorded += 1

                print(f"  [{recorded_this_sign}/{needed}] Saved: {os.path.basename(out_path)} "
                      f"({frame_count} frames)")

    cap.release()
    cv2.destroyAllWindows()

    print(f"\n{'='*60}")
    print(f"  Done! Recorded {total_recorded} total clips.")
    print(f"{'='*60}")
    _print_next_steps(total_recorded)


def _print_next_steps(total_recorded):
    if total_recorded > 0:
        print("\nNEXT STEPS:")
        print("  1. python preprocess.py   <- extract keypoints from new videos")
        print("  2. python augment.py      <- augment all samples (skips existing)")
        print("  3. python train.py        <- retrain model")
    else:
        print("\nNo clips recorded. Run again when ready.")


if __name__ == "__main__":
    record_signs()
