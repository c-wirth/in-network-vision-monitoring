import threading
import time
from application.components.Consumers import Consumers
from application.services.notification_service import NotificationService
from core.MLProcessingModule.MLModuleInterface import MLModuleInterface


class ClipIngestionService:
    """
    Polls clips from ML module, saves to disk, and records metadata in DB.
    """

    def __init__(self, ml_interface: MLModuleInterface, db_interface, notification_service: NotificationService, poll_interval=0.1):
        self.ml_interface = ml_interface
        self.db_interface = db_interface
        self.notification_service = notification_service
        self.poll_interval = poll_interval
        self._running = False
        self._thread = None
        self._latest_clip = None

        # Register as consumer
        self.ml_interface.register_consumer(Consumers.Clip_Ingestion)

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
        """
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
        """
        while self._running:
            # clip_data = self.ml_interface._clip_manager.poll_clip_data(Consumers.Clip_Ingestion)
            clip_data = self.ml_interface.poll_clip(Consumers.Clip_Ingestion)
            # clip_data = self.ml_interface.poll_clip(Consumers.Clip_Ingestion.name)
            # if clip_data:
            #     print(f"[DEBUG] got clip: {clip_data['clip_name']}, frames={len(clip_data['frames'])}")
            # else:
            #     print("[DEBUG] no clip")

            if clip_data:
                self._latest_clip = clip_data
                self.process_clip()

            time.sleep(self.poll_interval)

    def process_clip(self, test=False, test_clip_path=None):
        if test:
            clip = self.db_interface.create_clip_from_file(test_clip_path)
        else:
            clip = self.db_interface.create_clip_from_frames(self._latest_clip)


    # def process_clip(self, test=False, test_clip_path=None):
    #     save_root = Path("~/Desktop/stream_output").expanduser()
    #
    #     if test and test_clip_path:
    #         # simulate clip from existing file
    #         clip_name = Path(test_clip_path).stem
    #         clip_dir = save_root / clip_name
    #         clip_dir.mkdir(parents=True, exist_ok=True)
    #
    #         # copy file into clip folder
    #         target_path = clip_dir / Path(test_clip_path).name
    #         shutil.copy(test_clip_path, target_path)
    #
    #     else:
    #         # normal pipeline
    #         clip_name = self._latest_clip.get("clip_name", "unnamed_clip")
    #         clip_dir = save_root / clip_name
    #         clip_dir.mkdir(parents=True, exist_ok=True)
    #
    #         for idx, frame_bytes in enumerate(self._latest_clip.get("frames", [])):
    #             frame_path = clip_dir / f"frame_{idx:04d}.jpg"
    #             image = Image.open(io.BytesIO(frame_bytes))
    #             image.save(frame_path)
    #
    #     # DB SAVE (same for both)
    #     file_path = str(clip_dir)
    #     clip = self.db_interface.create_clip(file_path=file_path)


