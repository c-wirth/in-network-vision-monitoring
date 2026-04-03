# application/services/ClipIngestionService.py
import threading
import time
from application.components.Consumers import Consumers
from core.MLProcessingModule.MLModuleInterface import MLModuleInterface

from pathlib import Path
from PIL import Image
import io

class ClipIngestionService:
    """
    Polls the latest clip from the MLModuleInterface periodically.
    """

    def __init__(self, ml_interface: MLModuleInterface, poll_interval=0.01):
        self.ml_interface = ml_interface
        self.poll_interval = poll_interval
        self._running = False
        self._thread = None
        self._latest_clip = None

        # Register as a consumer in the module
        self.ml_interface._clip_manager.register_consumer(Consumers.Clip_Ingestion)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            print("[ClipIngestionService] Started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        self.ml_interface._clip_manager.unregister_consumer(Consumers.Clip_Ingestion)
        print("[ClipIngestionService] Stopped.")

    def _run(self):
        '''
            clip_data: Dict[str, Any] = {
                "clip_name": "example_clip",
                "frames": [frame_bytes],
                "width": frame_width,
                "height": frame_width,
                "fps": 30,
                "confidence": detection_confidence
            }
        '''

        print("In ClipIngestionService._run")
        while self._running:
            clip_data = self.ml_interface._clip_manager.poll_clip_data(Consumers.Clip_Ingestion)
            if clip_data:
                self._latest_clip = clip_data
                self.send_clip(test=True)

            time.sleep(self.poll_interval)


    def send_clip(self, test=False):

        if test:
                save_root = Path("~/Desktop/stream_output").expanduser()
                clip_name = self._latest_clip.get("clip_name", "unnamed_clip")
                clip_dir = save_root / clip_name
                clip_dir.mkdir(exist_ok=True)

                # Save frames
                for idx, frame_bytes in enumerate(self._latest_clip.get("frames", [])):
                    frame_path = clip_dir / f"frame_{idx:04d}.jpg"
                    image = Image.open(io.BytesIO(frame_bytes))
                    image.save(frame_path)


        else:
            print("[WARNING] CLIP INGESTION CLIP SENDING LOGIC NOT IMPLEMENTED")
