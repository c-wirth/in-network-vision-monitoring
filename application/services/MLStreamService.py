# application/services/MLStreamService.py
import threading
import time
from application.components.Consumers import Consumers

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

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            print("[MLStreamService] Started.")

    def stop(self):
        self._running = False
        if self._thread:
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
                try:
                    # Send frame/clip to ML module
                    self.ml_module_interface.process_frame(frame_bytes)
                except Exception as e:
                    print(f"[MLStreamService] Error processing frame {frame_idx}: {e}")
            time.sleep(self.poll_interval)
