# core/MLProcessingModule/components/FrameReceiver.py
import threading
import time
import copy
from datetime import datetime, timezone
import uuid
from PIL import Image
from io import BytesIO
from .MLEventBus import BusEvents, EventBus

DETECTION_INTERVAL = 30  # Push to detector every N frames

class FrameReceiver:
    def __init__(self, bus: EventBus, buffer_size, buffer_timeout_sec=1.0):
        self.buffer_size = buffer_size
        self.frame_buffer = [None] * buffer_size
        self.write_idx = 0
        self.frame_count = 0                    # counts every frame received
        self.buffer_timeout_sec = buffer_timeout_sec
        self.buffer_lock = threading.Lock()
        self._clip_in_progress = False          # guard against overlapping clips
        self.bus = bus
        self.bus.subscribe(BusEvents.ON_DETECTION, self._on_detection)
        self.frame_shape = None

    def _initialize_frame_shape(self, frame_bytes):
        img = Image.open(BytesIO(frame_bytes))
        self.frame_shape = (img.width, img.height, len(img.getbands()))
        print(f"[FrameReceiver] Frame shape initialized: {self.frame_shape}")

    def receive(self, frame_bytes):
        """Insert frame into circular buffer."""
        if self.frame_shape is None:
            self._initialize_frame_shape(frame_bytes)

        with self.buffer_lock:
            self.frame_buffer[self.write_idx] = frame_bytes
            self.write_idx = (self.write_idx + 1) % self.buffer_size
            self.frame_count += 1
            should_push = (self.frame_count % DETECTION_INTERVAL == 0)

        if should_push:
            self.bus.publish(BusEvents.PUSH_FRAME_TO_DETECTION_MANAGER, frame_bytes)

    def _generate_clip_name(self):
        now = datetime.now(timezone.utc)
        short_id = uuid.uuid4().hex[:6]
        return now.strftime(f"clip_%Y%m%d_%H%M%S_{short_id}")

    def _on_detection(self, confidence):
        """
        Called when a detection event fires.
        Snapshots the buffer immediately, then publishes CLIP_READY.
        Skips if a clip is already being processed.
        """
        # Guard: skip if a clip build is already running
        with self.buffer_lock:
            if self._clip_in_progress:
                print("[FrameReceiver] Detection fired but clip already in progress — skipping.")
                return
            self._clip_in_progress = True

            # Snapshot the buffer right now, before any more frames arrive
            frames_snapshot = copy.deepcopy(
                self.frame_buffer[self.write_idx:] +
                self.frame_buffer[:self.write_idx]
            )
            frames_snapshot = [f for f in frames_snapshot if f is not None]

        def build_and_publish():
            try:
                # If buffer wasn't full yet, wait briefly for remaining frames
                if len(frames_snapshot) < self.buffer_size:
                    print(f"[FrameReceiver] Buffer partially filled ({len(frames_snapshot)}/{self.buffer_size}), "
                          f"using available frames.")

                width, height, _ = self.frame_shape if self.frame_shape else (None, None, None)
                clip_data = {
                    "clip_name": self._generate_clip_name(),
                    "frames": frames_snapshot,
                    "width": width,
                    "height": height,
                    "fps": 30,
                    "confidence": confidence,
                }
                print(f"[FrameReceiver] Publishing CLIP_READY: {clip_data['clip_name']} "
                      f"({len(frames_snapshot)} frames)")
                self.bus.publish(BusEvents.CLIP_READY, clip_data)
            finally:
                with self.buffer_lock:
                    self._clip_in_progress = False

        threading.Thread(target=build_and_publish, daemon=True).start()
