import threading
from .IngestionEventBus import BusEvents


class StreamManager:
    def __init__(self, bus, max_frames=128):
        self.max_frames = max_frames
        self._buffer = [None] * self.max_frames
        self._next_idx = 0  # internal write index
        self._consumer_cursors = {}  # consumer_name -> last read index
        self._lock = threading.Lock()
        self.bus = bus
        self.bus.subscribe(BusEvents.FRAME_READY, self._handle_new_frame)

    def register_consumer(self, name):
        with self._lock:
            self._consumer_cursors[name] = None  # no frames seen yet

    def unregister_consumer(self, name):
        with self._lock:
            self._consumer_cursors.pop(name, None)

    def _handle_new_frame(self, data):
        frame_id = data["frame_id"]
        frame = data["frame"]
        self._push_frame(frame_id, frame)

    def _push_frame(self, frame_id, frame):
        with self._lock:
            self._buffer[self._next_idx] = {"frame_id": frame_id, "frame": frame}
            self._next_idx = (self._next_idx + 1) % self.max_frames

    def poll_frame(self, consumer_name):
        with self._lock:
            last_idx = self._consumer_cursors.get(consumer_name)

            # Determine next index to read
            if last_idx is None:
                # First poll: read the oldest frame in buffer
                idx = (self._next_idx - 1) % self.max_frames
            else:
                idx = (last_idx + 1) % self.max_frames

            slot = self._buffer[idx]
            if slot is None:
                return None, None

            last_frame_id = None if last_idx is None else self._buffer[last_idx]["frame_id"]
            current_frame_id = slot["frame_id"]

            #print(f"[DEBUG StreamManager] consumer={consumer_name} last_frame_id={last_frame_id} current_frame_id={current_frame_id}")

            # Only return if frame_id is new
            if last_frame_id == current_frame_id:
                return None, None

            # Move cursor forward
            self._consumer_cursors[consumer_name] = idx
            return current_frame_id, slot["frame"]
