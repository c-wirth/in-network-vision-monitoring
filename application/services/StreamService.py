# StreamService.py
import os
import time
import threading
from application.components import Consumers


class StreamService:
    """
    Consumer service that polls frames from the IngestionModuleInterface
    and writes them to a directory (simulating a live stream for the frontend).
    """

    def __init__(self, ingestion_interface, output_dir="stream_output", poll_interval=0.01):
        """
        :param ingestion_interface: Instance of IngestionModuleInterface
        :param output_dir: Where to save frames
        :param poll_interval: How often to poll frames (seconds)
        """
        self.ingestion_interface = ingestion_interface
        self.output_dir = output_dir
        self.poll_interval = poll_interval

        # Internal control
        self._running = False
        self._thread = None

        os.makedirs(self.output_dir, exist_ok=True)

        # Register as a consumer
        self.ingestion_interface.register_consumer(Consumers.Streamer)

    def start(self):
        """Start polling frames in a separate thread."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            print("[StreamService] Started.")

    def stop(self):
        """Stop polling frames."""
        self._running = False
        if self._thread:
            self._thread.join()
            print("[StreamService] Stopped.")

        # Optional: unregister consumer
        self.ingestion_interface.unregister_consumer(Consumers.Streamer)

    def _run(self):
        """Polling loop that saves frames to the output directory."""
        while self._running:
            frame_idx, frame = self.ingestion_interface.poll_frame(Consumers.Streamer)
            if frame is not None:
                self._save_frame(frame_idx, frame)
            else:
                print("DEBUG: NO FRAME RECEIVED IN StreamService._run()")
            time.sleep(self.poll_interval)


    def _save_frame(self, frame_idx, frame_bytes):
        """
        Save a frame to the output directory.
        Frame filename includes internal index to preserve order.
        """
        filename = os.path.join(self.output_dir, f"frame_{frame_idx:04d}.bin")
        with open(filename, "wb") as f:
            f.write(frame_bytes)
        print(f"DEBUG [StreamService] Saved frame {frame_idx}")
