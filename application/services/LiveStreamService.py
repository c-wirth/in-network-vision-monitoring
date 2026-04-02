# LiveStreamService.py
import threading
import time
from application.components.Consumers import Consumers

class LiveStreamService:
    """
    Polls frames from IngestionModuleInterface and keeps the latest frame in memory.
    """

    def __init__(self, ingestion_interface, poll_interval=0.01):
        self.ingestion_interface = ingestion_interface
        self.poll_interval = poll_interval

        # Internal control
        self._running = False
        self._thread = None

        # In-memory storage for the latest frame
        self._latest_frame = None
        self._latest_index = -1
        self._lock = threading.Lock()

        # Register as a consumer
        self.ingestion_interface.register_consumer(Consumers.Streamer)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            print("[LiveStreamService] Started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        self.ingestion_interface.unregister_consumer(Consumers.Streamer)
        print("[LiveStreamService] Stopped.")

    def _run(self):
        while self._running:
            frame_idx, frame_bytes = self.ingestion_interface.poll_frame(Consumers.Streamer)
            if frame_bytes:
                # Save latest frame in memory
                with self._lock:
                    self._latest_frame = frame_bytes
                    self._latest_index = frame_idx
            time.sleep(self.poll_interval)

    def get_latest_frame(self):
        """
        Returns the latest frame in memory (thread-safe)
        """
        with self._lock:
            return self._latest_index, self._latest_frame


    def frame_generator(self):
        """
        Generator for MJPEG streaming. Yields frames continuously in MJPEG format.
        """
        while self._running:
            _, frame_bytes = self.get_latest_frame()
            if frame_bytes:
                # Yield frame in MJPEG multipart format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(self.poll_interval)
