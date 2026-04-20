# core/MLProcessingModule/components/DetectionManager.py
from .MLEventBus import BusEvents, EventBus
from ultralytics import YOLO
import numpy as np
from PIL import Image
from io import BytesIO



class DetectionManager:
    """
    Performs object detection on incoming frames and publishes confidence events.
    """

    def __init__(self, confidence_threshold: float, bus: EventBus, model_path="models/yolov8n.pt", device="cpu"):
        self.bus = bus
        self.confidence_threshold = confidence_threshold

        self.model = YOLO(model_path)
        self.model.to(device)
        print(f"[DetectionManager] Loaded YOLOv8 model from {model_path}")

        # Subscribe to frame events
        self.bus.subscribe(BusEvents.PUSH_FRAME_TO_DETECTION_MANAGER, self._perform_detection)

    def _perform_detection(self, frame_bytes: bytes):
        """
        Perform detection on a single frame.
        Only considers 'person' class (COCO cls=0).
        Publishes ON_DETECTION event with max human confidence.
        """
        #print("[DEBUG] in DetectionManager._perform_detection")

        # Load and resize image
        img = Image.open(BytesIO(frame_bytes)).convert("RGB")
        img = img.resize((640, 640))
        img_np = np.array(img)

        # Run YOLOv8 prediction
        results = self.model.predict(img_np, verbose=False)

        # Find max confidence for 'person' class
        max_human_conf = 0.0
        for r in results:
            if r.boxes is not None and len(r.boxes) > 0:
                cls_ids = r.boxes.cls.cpu().numpy()  # class indices
                confs = r.boxes.conf.cpu().numpy()   # confidences
                for cls_id, conf in zip(cls_ids, confs):
                    if int(cls_id) == 0:  # COCO 'person'
                        max_human_conf = max(max_human_conf, float(conf))

        # Publish if above threshold
        if max_human_conf >= self.confidence_threshold:
            print(f"[DetectionManager] Frame detected with confidence of {max_human_conf:.2f}")
            self.bus.publish(BusEvents.ON_DETECTION, float(max_human_conf))
        else:
            pass
            #print(f"[DetectionManager] No humans above threshold. Max confidence: {max_human_conf:.2f}")
