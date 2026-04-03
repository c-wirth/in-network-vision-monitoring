# core.MLProcessingModule.MLModuleInterface.py

from collections import defaultdict
from components import EventBus, BusEvents, FrameReceiver, DetectionService, ClipProcessor

class MLModuleInterface:

    def __init__(self,ml_cfg: defaultdict, bus: EventBus):

        self.ml_cfg = ml_cfg
        self.bus = bus

        # Configuration
        self.sample_rate_frames = ml_cfg.get("sample_rate_frames", 15)  # e.g., take every 15th frame
        self.grace_period_cycles = ml_cfg.get("grace_period_cycles", 8) # number of detection cycles to keep recording
        self.confidence_threshold = ml_cfg.get("confidence_threshold", 0.5)
        self.max_clip_length = ml_cfg.get("max_clip_length", 300)

        # Components
        self.frame_receiver = FrameReceiver(
            internal_frame_buffer_sz =self.sample_rate_frames * (self.grace_period_cycles),
            bus=bus
        )

        #TODO these functions will need parameters when implemented
        self.detection_service = DetectionService()
        self.clip_processor = ClipProcessor()

        # Internal state
        self._recording = False
        self._grace_counter = 0

    def process_frame(self, frame_bytes):
        """Entry point for new frames from MLStreamService"""
        self.frame_receiver.receive(frame_bytes)

