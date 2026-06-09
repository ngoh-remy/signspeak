import numpy as np

def normalize_keypoints(sequence):
    """
    Zero-centers the coordinates of each frame relative to the nose (pose[0]).
    This removes absolute screen position dependency and prevents overfitting.
    sequence shape: (frames, 258)
    """
    normalized_seq = np.copy(sequence)
    for i in range(len(normalized_seq)):
        frame = normalized_seq[i]
        # Check if pose exists (nose visibility > 0)
        if frame[3] > 0:
            nose_x, nose_y, nose_z = frame[0], frame[1], frame[2]
            
            # Normalize Pose (132 elements -> 33 landmarks * 4)
            for j in range(0, 132, 4):
                if frame[j+3] > 0: # If visible
                    frame[j]   -= nose_x
                    frame[j+1] -= nose_y
                    frame[j+2] -= nose_z
                    
            # Normalize Left Hand (63 elements -> 21 landmarks * 3) starting at index 132
            # Left hand exists if sum != 0
            if np.sum(frame[132:195]) != 0:
                for j in range(132, 195, 3):
                    frame[j]   -= nose_x
                    frame[j+1] -= nose_y
                    frame[j+2] -= nose_z
                    
            # Normalize Right Hand (63 elements -> 21 landmarks * 3) starting at index 195
            if np.sum(frame[195:258]) != 0:
                for j in range(195, 258, 3):
                    frame[j]   -= nose_x
                    frame[j+1] -= nose_y
                    frame[j+2] -= nose_z
                    
    return normalized_seq
