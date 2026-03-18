import threading
from collections import deque

class StreamManager:
    def __init__(self, bus, max_frames=256):
        self.max_frames = max_frames
        self.buffer = [None] * self.max_frames
        self.frame_id = -1  # will wrap to 0 on first frame

        self.consumer_cursors = {}  # {consumer_name: frame_id}
        self.lock = threading.Lock()


        self.bus = bus
        self.bus.subscribe(BusEvents.FRAME_READY, self._handle_new_frame)

    def register_consumer(self, name):
        with self.lock:
            self.consumer_cursors[name] = self.frame_id

    def unregister_consumer(self, name):
        with self.lock:
            if name in self.consumer_cursors:
                del self.consumer_cursors[name]


    def _handle_new_frame(self, data):
        self._push_frame(data["frame"])

    def _push_frame(self, frame):
        """
        Push a new frame into the buffer.
        frame_id wraps every 256 frames.
        """
        with self.lock:
            self.frame_id = (self.frame_id + 1) % 256
            idx = self.frame_id % self.max_frames
            self.buffer[idx] = frame

    def poll_frame(self, consumer_name):
        """
        Consumer polls next frame.
        Returns (frame_id, frame) or (None, None) if no new frame.
        """
        with self.lock:
            last_seen = self.consumer_cursors.get(consumer_name, None)
            if last_seen is None:
                return None, None

            # compute next frame_id
            next_frame_id = (last_seen + 1) % 256
            idx = next_frame_id % self.max_frames
            frame = self.buffer[idx]

            if frame is None:
                return None, None

            self.consumer_cursors[consumer_name] = next_frame_id
            return next_frame_id, frame
