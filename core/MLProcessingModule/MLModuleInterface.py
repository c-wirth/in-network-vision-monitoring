# core.MLProcessingModule.MLModuleInterface.py

from collections import defaultdict
from .components import EventBus, BusEvents, FrameReceiver,  DetectionManager, ClipManager

class MLModuleInterface:

    def __init__(self,ml_cfg: defaultdict):

        self.ml_cfg = ml_cfg
        self.bus = EventBus()

        # Configuration
        self.confidence_threshold = ml_cfg.get("confidence_threshold", 0.5)
        self.max_clip_length = ml_cfg.get("max_clip_length", 300)
        self.buffer_timeout_sec= ml_cfg.get("buffer_timeout_sec", 1.0)

        # Components
        self.frame_receiver = FrameReceiver(
            buffer_size=self.max_clip_length,
            bus=self.bus,
            buffer_timeout_sec=self.buffer_timeout_sec
        )

        self._detection_service = DetectionManager(confidence_threshold=self.confidence_threshold, bus=self.bus)
        self._clip_manager = ClipManager(bus=self.bus)


    def register_consumer(self, consumer: "Consumer"):
        """
        Register a new consumer to start receiving frames.
        """
        self._clip_manager.register_consumer(consumer.name)


    def unregister_consumer(self, consumer: "Consumer"):
        """
        Unregister a consumer to stop receiving frames.
        """
        self._clip_manager.unregister_consumer(consumer.name)


    def poll_clip(self, consumer: "Consumer"):
        """
        Poll the next available clip for a given consumer.
        Returns clip
        """
        return self._clip_manager.poll_clip(consumer.name)


    def process_frame(self, frame_bytes):
        """Entry point for new frames from MLStreamService"""
        self.frame_receiver.receive(frame_bytes)
