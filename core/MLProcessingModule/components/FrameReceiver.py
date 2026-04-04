# core/MLProcessingModule/components/FrameReceiver.py
import threading
import time
import copy
from datetime import datetime, timezone
import uuid
from PIL import Image
from io import BytesIO

from .MLEventBus import BusEvents, EventBus

class FrameReceiver:

    def __init__(self, bus: EventBus, buffer_size, buffer_timeout_sec=1.0):
        self.buffer_size = buffer_size
        self.frame_buffer = [None] * buffer_size
        self.write_idx = 0  # pointer to next write
        self.buffer_timeout_sec = buffer_timeout_sec
        self.buffer_lock = threading.Lock()

        self.bus = bus
        self.bus.subscribe(BusEvents.ON_DETECTION, self._on_detection)

        self.frame_shape = None


    def _initialize_frame_shape(self, frame_bytes):
        """Call this once at startup to get dimensions."""
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

        # If pointer wrapped back to 0, push the latest frame to detector

        if self.write_idx -1 == 0 and self.bus:
            #print(f"[DEBUG] idx: {self.write_idx} publishing ") 
            self.bus.publish(BusEvents.PUSH_FRAME_TO_DETECTION_MANAGER, frame_bytes)


    def _generate_clip_name(self):
        now = datetime.now(timezone.utc)
        short_id = uuid.uuid4().hex[:6]
        return now.strftime(f"clip_%Y%m%d_%H%M%S_{short_id}")


    def _on_detection(self, confidence):
        """
        Called when detection happens.
        - Wait until buffer is full or timeout occurs.
        - Build clip_data dictionary
        - Publish to bus
        """

        def wait_for_buffer():
            start_time = time.time()

            while True:
                with self.buffer_lock:
                    buffer_full = None not in self.frame_buffer

                    if buffer_full:
                        frames = copy.deepcopy(
                            self.frame_buffer[self.write_idx:] +
                            self.frame_buffer[:self.write_idx]
                        )
                    else:
                        frames = None

                if frames is not None:
                    break

                if time.time() - start_time >= self.buffer_timeout_sec:
                    with self.buffer_lock:
                        frames = copy.deepcopy(self.frame_buffer[:self.write_idx])
                    break

                time.sleep(0.01)

            # ---- Build clip dictionary ----
            width, height, _ = self.frame_shape if self.frame_shape else (None, None, None)

            clip_data = {
                "clip_name": self._generate_clip_name(),
                "frames": frames,
                "width": width,
                "height": height,
                "fps": 30,  # could also come from config
                "confidence": confidence,
            }

            # ---- Publish clip ----
            self.bus.publish(BusEvents.CLIP_READY, clip_data)


        threading.Thread(target=wait_for_buffer, daemon=True).start()
