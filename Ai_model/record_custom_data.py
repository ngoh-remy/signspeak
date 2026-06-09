import cv2
import os
import time

SL_PATH = os.path.join(os.path.dirname(__file__), "SL")
FRAMES_PER_VIDEO = 30
FPS = 30

print("=" * 60)
print("  SignSpeak Personal Video Recorder")
print("=" * 60)
print("Type the name of the sign you want to record.")
print("Example: 'yes', 'no', 'drink', 'help', 'go'")
print("Type 'quit' to exit.")

while True:
    gesture = input("\nEnter sign to record (or 'quit'): ").strip().lower()
    if gesture == 'quit':
        break
    if not gesture:
        continue
        
    gesture_dir = os.path.join(SL_PATH, gesture)
    os.makedirs(gesture_dir, exist_ok=True)
    
    videos_recorded = 0
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print(f"\nReady to record '{gesture}'!")
    print("- Press SPACE to record exactly 1 second (30 frames)")
    print("- Press 'q' to stop recording this sign and choose another")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
            
        frame = cv2.flip(frame, 1) # Mirror display
        
        # Draw HUD
        cv2.putText(frame, f"Sign: {gesture.upper()}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Recorded this session: {videos_recorded}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, "Press SPACE to start recording", (10, 450), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
        cv2.imshow("SignSpeak Recorder", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            # 3 second countdown
            for countdown in range(3, 0, -1):
                t_end = time.time() + 1
                while time.time() < t_end:
                    ret, c_frame = cap.read()
                    if not ret: break
                    c_frame = cv2.flip(c_frame, 1)
                    # Show countdown HUD
                    cv2.putText(c_frame, f"Starting in {countdown}...", (150, 240), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 165, 255), 4)
                    cv2.imshow("SignSpeak Recorder", c_frame)
                    cv2.waitKey(10)
            
            # Start Recording
            filename = os.path.join(gesture_dir, f"personal_{int(time.time())}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filename, fourcc, FPS, (640, 480))
            
            print(f"Recording {FRAMES_PER_VIDEO} frames...", end=" ")
            for i in range(FRAMES_PER_VIDEO):
                ret, r_frame = cap.read()
                if not ret: break
                r_frame = cv2.flip(r_frame, 1)
                
                # Write clean frame (no text) to video
                out.write(r_frame)
                
                # Show recording status on screen
                display_frame = r_frame.copy()
                cv2.putText(display_frame, f"RECORDING: {i+1}/{FRAMES_PER_VIDEO}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                cv2.imshow("SignSpeak Recorder", display_frame)
                cv2.waitKey(int(1000/FPS)) # Approx 30fps wait
                
            out.release()
            videos_recorded += 1
            print(f"Saved: {filename}")
            
    cap.release()
    cv2.destroyAllWindows()
