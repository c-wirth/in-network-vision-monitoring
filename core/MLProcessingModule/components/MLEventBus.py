from collections import defaultdict

class BusEvents:
    FRAME_TO_ML_MODULE = "frame_to_ml_module"
    #FRAME_READY    = "frame_ready"


import threading

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
