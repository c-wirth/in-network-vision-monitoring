# application/services/LiveStreamService.py
import threading
import time
from application.components.Consumers import Consumers

print("LIVE STREAM FILE LOADED")
class LiveStreamService:
    """
    Polls frames from IngestionModuleInterface and keeps the latest frame in memory.
    """

    def __init__(self, ingestion_interface, poll_interval=0.01):

        # change this to True when using a looping .mp4 file for the feed
        # change this to false to use the actual camera
        self.test_mode = True

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
        self.ingestion_interface.register_consumer(Consumers.Live_Stream)

    def _run_test_mode(self):
        import cv2

        video_path = r"C:\Users\fletc\OneDrive\Desktop\clip_of_sean\IMG_0858.mp4"
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"[LiveStream] ERROR opening video: {video_path}")
            return

        print("[LiveStream] Test mode video started")

        while self._running:
            ret, frame = cap.read()

            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            success, buffer = cv2.imencode(".jpg", frame)
            if not success:
                continue

            frame_bytes = buffer.tobytes()

            with self._lock:
                self._latest_frame = frame_bytes
                self._latest_index = 0

            time.sleep(self.poll_interval)

        cap.release()
        print("[LiveStream] Test mode video stopped")

    def start(self):
        print("[LiveStream] THREAD STARTED")
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            print("[LiveStreamService] Started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        self.ingestion_interface.unregister_consumer(Consumers.Live_Stream)
        print("[LiveStreamService] Stopped.")

    def _run(self):
        if self.test_mode:
            self._run_test_mode()
            return
        while self._running:
            print("[LiveStream] polling...")
            frame_idx, frame_bytes = self.ingestion_interface.poll_frame(Consumers.Live_Stream)
            if frame_bytes:
                print("[LiveStream] got frame")
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

