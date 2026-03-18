# EventBus.py
from collections import defaultdict

class BusEvents:
    CONTROL_SIGNAL = "control_signal"
    FRAME_RECEIVED = "frame_received"
    START_STREAM   = "start_stream"
    STOP_STREAM    = "stop_stream"
    FRAME_READY    = "frame_ready"


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
