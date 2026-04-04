import cv2
import os
import sys
import time

# Usage: python3 view_frames.py frames_folder
if len(sys.argv) < 2:
    print("Usage: python3 view_frames.py frames_folder")
    sys.exit(1)

frames_folder = sys.argv[1]

# Get all image files in folder and sort
frame_files = sorted([
    os.path.join(frames_folder, f)
    for f in os.listdir(frames_folder)
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
])

if not frame_files:
    print(f"No image files found in {frames_folder}")
    sys.exit(1)

fps = 30
delay = 1 / fps  # seconds per frame

for frame_file in frame_files:
    frame = cv2.imread(frame_file)
    if frame is None:
        continue

    cv2.imshow("Video Frames", frame)
    
    # Wait for delay, break if 'q' is pressed
    if cv2.waitKey(int(delay * 1000)) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
