from .MLEventBus import BusEvents, EventBus


class DetectionManager:

    def __init__(self, confidence_threshold, bus: EventBus):
        self.bus = bus
        self.confidence_threshold=confidence_threshold
        self.bus.subscribe(BusEvents.PUSH_FRAME_TO_DETECTION_MANAGER, self._perform_detection)

    def _perform_detection(self, frame_bytes):
        print("[DEBUG] in DetectionManager._perform_detection")



        score = 0.75
        self.bus.publish(BusEvents.ON_DETECTION, score)

'''

        clip_data: Dict[str, Any] = {
            "clip_name": "example_clip",
            "frames": [frame_bytes],
            "width": frame_width,
            "height": frame_width,
            "fps": 30,
            "confidence": detection_confidence
        }

'''
