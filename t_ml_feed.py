from pathlib import Path
import time

from core.MLProcessingModule.MLModuleInterface import MLModuleInterface
from application.services.ClipIngestionService import ClipIngestionService
from core.db_infrastructure.db_interface import DBInterface
from application.services.notification_service import NotificationService

ml = MLModuleInterface(ml_cfg={"confidence_threshold": 0.0})

db = DBInterface()

notification_service = NotificationService()

ingestion = ClipIngestionService(
    ml,
    db,
    notification_service=notification_service
)
ingestion.start()

folder = Path(r"C:\Users\fletc\OneDrive\Desktop\test_frames")

for img_path in folder.glob("*.jpg"):
    with open(img_path, "rb") as f:
        ml.process_frame(f.read())
    time.sleep(0.1)

time.sleep(5)