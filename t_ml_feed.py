from pathlib import Path
import time
import cv2

from core.MLProcessingModule.MLModuleInterface import MLModuleInterface
from application.services.ClipIngestionService import ClipIngestionService
from core.db_infrastructure.db_interface import DBInterface
from application.services.notification_service import NotificationService

# ------------------------
# Setup services
# ------------------------
ml = MLModuleInterface(ml_cfg={"confidence_threshold": 0.0})
db = DBInterface()
notification_service = NotificationService()

ingestion = ClipIngestionService(
    ml,
    db,
    notification_service=notification_service
)

ingestion.start()

# ------------------------
# Video input (MP4)
# ------------------------
video_path = Path(r"C:\Users\fletc\OneDrive\Desktop\clip_of_sean\IMG_0851.mp4")

cap = cv2.VideoCapture(str(video_path))

if not cap.isOpened():
    print(f"[ERROR] Could not open video: {video_path}")
    exit()

print("[INFO] Starting video feed simulation...")

# ------------------------
# Feed frames into ML
# ------------------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    success, buffer = cv2.imencode(".jpg", frame)
    if not success:
        continue

    ml.process_frame(buffer.tobytes())

    time.sleep(0.1)

cap.release()

print("[INFO] Finished feeding video. Waiting for ingestion...")

# give ingestion time to build and save clip
time.sleep(5)

print("[INFO] Done.")