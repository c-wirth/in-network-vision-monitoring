import cv2
import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Simple image sequence viewer")
    parser.add_argument("fps", type=int, help="Frames per second")
    parser.add_argument("directory", type=str, help="Directory containing images")

    args = parser.parse_args()

    fps = args.fps
    image_dir = args.directory
    delay = int(1000 / fps)

    if not os.path.isdir(image_dir):
        print(f"Error: Directory '{image_dir}' does not exist.")
        sys.exit(1)

    images = sorted([
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])

    if not images:
        print("No images found in directory.")
        sys.exit(1)

    index = 0
    playing = True

    while True:
        img = cv2.imread(images[index])
        cv2.imshow("Viewer", img)

        key = cv2.waitKey(delay if playing else 0) & 0xFF

        if key == ord('q'):
            break
        elif key == ord(' '):  # Spacebar toggle play/pause
            playing = not playing
        elif key == 81:  # Left arrow
            index = max(0, index - 1)
        elif key == 83:  # Right arrow
            index = min(len(images) - 1, index + 1)

        if playing:
            index = (index + 1) % len(images)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
