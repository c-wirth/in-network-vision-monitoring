import threading
import time
from datetime import timedelta
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
        print("[DEBUG] starting CLipIngestionService._run()")
        while self._running:
            # clip_data = self.ml_interface._clip_manager.poll_clip_data(Consumers.Clip_Ingestion)
            # clip_data = self.ml_interface.poll_clip(Consumers.Clip_Ingestion.name)

            clip_data = self.ml_interface.poll_clip(Consumers.Clip_Ingestion)
            if clip_data:
                print(f"[ClipIngestionService DEBUG] got clip: {clip_data['clip_name']}, frames={len(clip_data['frames'])}")
            else:
                #print("[ClipIngestionService DEBUG] no clip")
                pass

            if clip_data:
                self._latest_clip = clip_data
                self.process_clip()

            time.sleep(self.poll_interval)

    def process_clip(self, test=False, test_clip_path=None):
        if test:
            clip = self.db_interface.create_clip_from_file(test_clip_path)
        else:
            clip = self.db_interface.create_clip_from_frames(self._latest_clip)

        # ------------------------
        # SEND NOTIFICATION
        # ------------------------
        user = self.db_interface.get_user_by_role("primary")

        print("[DEBUG] primary user:", user)
        print("[DEBUG] email:", user.email if user else None)

        COOLDOWN = timedelta(minutes=2)

        if user and user.email:
            clips = self.db_interface.get_recent_clips(limit=2)

            if len(clips) < 2:
                print("[Notification] Sent (first clip)")
                self.notification_service.send_clip_alert(
                    user.email,
                    clip.file_path
                )
            else:
                current_clip = clips[0]
                previous_clip = clips[1]

                time_diff = current_clip.created_at - previous_clip.created_at

                if time_diff > COOLDOWN:
                    print("[Notification] Sent")
                    self.notification_service.send_clip_alert(
                        user.email,
                        clip.file_path
                    )
                else:
                    print("[Notification] Skipped (cooldown active)")



