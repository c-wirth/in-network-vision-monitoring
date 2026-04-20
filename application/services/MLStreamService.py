# application/services/MLStreamService.py
import threading
import time
from pathlib import Path
from application.components.Consumers import Consumers
import os

class MLStreamService:
    """
    Polls frames/clips from IngestionModuleInterface and sends them to the MLModuleInterface.
    """

    def __init__(self, ingestion_interface, ml_module_interface, poll_interval=0.01):
        self.ingestion_interface = ingestion_interface
        self.ml_module_interface = ml_module_interface
        self.poll_interval = poll_interval

        # Control
        self._running = False
        self._thread = None

        # Register as a consumer for the ingestion interface
        self.ingestion_interface.register_consumer(Consumers.ML_Stream)

    def start(self, test=False):
        if not self._running:
            self._running = True

        if test:
            print("[INFO] Beginning Streaming test")
            self._thread = threading.Thread(
                target=self._run_test,
                args=(Path("~/Desktop/stream_test/").expanduser(), 30),
                daemon=True
            )
        else:
            self._thread = threading.Thread(target=self._run, daemon=True)

        self._thread.start()
        print("[MLStreamService] Started.")


    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
        self.ingestion_interface.unregister_consumer(Consumers.ML_Stream)
        print("[MLStreamService] Stopped.")


    def _run(self):
        """
        Poll frames/clips and send to the MLModuleInterface for processing.
        """
        while self._running:
            frame_idx, frame_bytes = self.ingestion_interface.poll_frame(Consumers.ML_Stream)
            if frame_bytes:
                #print("[MLStreamService DEBUG] Frame received!!")
                try:
                    # Send frame/clip to ML module
                    self.ml_module_interface.process_frame(frame_bytes)
                except Exception as e:
                    print(f"[MLStreamService] Error processing frame {frame_idx}: {e}")
            time.sleep(self.poll_interval)

        else:
            print("[MLStreamService DEBUG] No frame received")
            # no frame available, back off a bit to avoid busy-wait
            time.sleep(self.poll_interval)



    def _run_test(self, test_dir, test_fps):
        """
        Streams frames from a local directory as if they were coming from ingestion.
        """

        if not test_dir:
            raise ValueError("test_dir must be provided when test=True")

        frame_delay = 1.0 / test_fps

        # Load and sort files
        frame_files = sorted([
            f for f in os.listdir(test_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        print(f"[MLStreamService] Test mode: streaming {len(frame_files)} frames from {test_dir}")

        while self._running:
            for fname in frame_files:
                if not self._running:
                    break

                path = os.path.join(test_dir, fname)

                try:
                    with open(path, "rb") as f:
                        frame_bytes = f.read()

                    self.ml_module_interface.process_frame(frame_bytes)

                except Exception as e:
                    print(f"[MLStreamService] Test frame error: {e}")

                time.sleep(frame_delay)
