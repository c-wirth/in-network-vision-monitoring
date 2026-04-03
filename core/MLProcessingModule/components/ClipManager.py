from .MLEventBus import BusEvents, EventBus
import threading

class ClipManager:
    """
    Stores the latest clip_data and allows multiple consumers to poll it independently.
    """

    def __init__(self, bus: EventBus):
        self.bus = bus
        self._clip_data = None  # The most recent clip_data
        self._lock = threading.Lock()
        self._consumer_seen = {}  # consumer_name -> bool, has the consumer seen the clip_data

        # Subscribe to new clip_data events
        self.bus.subscribe(BusEvents.CLIP_READY, self._push_clip_data)


    def _push_clip_data(self, clip_data):
        """Update the current clip_data and mark it as unseen for all consumers."""
        print("[DEBUG] in CLipManager._push_clip_data pushing a clip")
        with self._lock:
            self._clip_data = clip_data
            self._consumer_seen = {k: False for k in self._consumer_seen}


    def register_consumer(self, name):
        """Add a new consumer."""
        with self._lock:
            self._consumer_seen[name] = True if self._clip_data is None else False


    def unregister_consumer(self, name):
        """Remove a consumer."""
        with self._lock:
            self._consumer_seen.pop(name, None)


    def poll_clip_data(self, name):
        """
        Return the latest clip_data for the given consumer.
        Only returns the clip_data if the consumer hasn't seen it yet.
        """
        with self._lock:
            if name not in self._consumer_seen:
                return None
            if self._clip_data is None or self._consumer_seen[name]:
                return None

            # Mark as seen and return
            self._consumer_seen[name] = True
            return self._clip_data
