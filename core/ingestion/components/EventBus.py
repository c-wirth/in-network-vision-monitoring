# EventBus.py
from collections import defaultdict

class BusEvents:
    CONTROL_SIGNAL = "control_signal"
    FRAME_RECEIVED = "frame_received"
    START_STREAM   = "start_stream"
    STOP_STREAM    = "stop_stream"
    FRAME_READY    = "frame_ready"


class EventBus:
    def __init__(self):
        # Dictionary: topic -> list of callbacks
        self._subscribers = defaultdict(list)

    def subscribe(self, topic, callback):
        """Register a callback for a specific topic."""
        self._subscribers[topic].append(callback)

    def publish(self, topic, payload=None):
        """Call all callbacks registered for this topic with the payload."""
        for callback in self._subscribers.get(topic, []):
            callback(payload)
