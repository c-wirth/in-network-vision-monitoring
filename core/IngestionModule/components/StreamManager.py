import threading
from collections import deque
from EventBus import BusEvents

class StreamManager:
    """
    Thread-safe circular buffer for frames.
    Preserves the original frame_id while using an internal index for storage.
    """

    def __init__(self, bus, max_frames=256):
        self.max_frames = max_frames
        self._buffer = [None] * self.max_frames
        self._next_idx = 0  # internal circular index for buffer placement

        self._consumer_cursors = {}  # {consumer_name: last_seen_frame_id}
        self._lock = threading.Lock()

        self.bus = bus
        self.bus.subscribe(BusEvents.FRAME_READY, self._handle_new_frame)

    def register_consumer(self, name):
        """
        Register a new consumer. Initially they haven't seen any frames.
        """
        with self._lock:
            self._consumer_cursors[name] = None

    def unregister_consumer(self, name):
        with self._lock:
            if name in self._consumer_cursors:
                del self._consumer_cursors[name]

    def _handle_new_frame(self, data):
        """
        Called by FrameParser when a full frame is ready.
        Expects data = {"frame_id": ..., "frame": ...}
        """
        frame_id = data["frame_id"]
        frame = data["frame"]
        self._push_frame(frame_id, frame)

    def _push_frame(self, frame_id, frame):
        """
        Push a frame into the internal circular buffer.
        Only the internal index wraps around; frame_id is preserved.
        """
        with self._lock:
            self._buffer[self._next_idx] = {"frame_id": frame_id, "frame": frame}
            self._next_idx = (self._next_idx + 1) % self.max_frames

    def poll_frame(self, consumer_name):
        """
        Return the next unseen frame for a consumer as (frame_id, frame),
        or (None, None) if there is no new frame.
        """
        with self._lock:
            last_seen_id = self._consumer_cursors.get(consumer_name)
            if last_seen_id is None and consumer_name not in self._consumer_cursors:
                return None, None

            # Search buffer for next unseen frame
            for i in range(self.max_frames):
                idx = (self._next_idx - 1 - i) % self.max_frames
                slot = self._buffer[idx]
                if slot is None:
                    continue
                if last_seen_id is None or slot["frame_id"] != last_seen_id:
                    # Next frame found
                    self._consumer_cursors[consumer_name] = slot["frame_id"]
                    return slot["frame_id"], slot["frame"]

            # No new frame found
            return None, None
