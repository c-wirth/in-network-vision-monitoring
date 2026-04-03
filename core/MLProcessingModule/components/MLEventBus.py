from collections import defaultdict
import threading

class BusEvents:
    PUSH_FRAME_TO_ML_MODULE = "push_frame_to_ml_module"
    ON_DETECTION = "on_detection"
    PUSH_SNAPSHOT_TO_BUILDER = "push_snapshot_to_builder"


class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, topic, callback):
        with self._lock:
            self._subscribers[topic].append(callback)

    def publish(self, topic, payload=None):
        with self._lock:
            callbacks = list(self._subscribers.get(topic, []))

        for callback in callbacks:
            callback(payload)
