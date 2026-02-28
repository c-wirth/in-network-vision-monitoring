import cv2
import glob
import os
import sys

# --- config ---
FPS = 5
FRAME_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("/Users/colby/Desktop/stream_test/20260227_210648")

# --- load frames in order ---
frame_paths = sorted(glob.glob(os.path.join(FRAME_DIR, "frame_*.jpg")))

if not frame_paths:
    print(f"No frames found in {FRAME_DIR}")
    sys.exit(1)

print(f"Playing {len(frame_paths)} frames at {FPS} FPS from {FRAME_DIR}")
print("Press 'q' to quit, space to pause")

delay_ms = int(1000 / FPS)
paused = False

for path in frame_paths:
    frame = cv2.imread(path)
    if frame is None:
        print(f"Could not read {path} — skipping")
        continue

    # Rotate frame 180 degrees
    frame = cv2.rotate(frame, cv2.ROTATE_180)

    cv2.imshow("Stream Playback", frame)

    while True:
        key = cv2.waitKey(0 if paused else delay_ms) & 0xFF

        if key == ord('q'):
            cv2.destroyAllWindows()
            sys.exit(0)

        elif key == ord(' '):
            paused = not paused
            if not paused:
                break

        else:
            break

cv2.destroyAllWindows()
print("Playback complete")
