# IngestionModule.py
from components import EventBus, UDPManager, FrameParser, StreamManager

class IngestionModule:
    def __init__(self, udp_cfg):

        self.bus = EventBus()

        self.udp_manager = UDPManager(udp_cfg, self.bus)
        self.frame_parser = FrameParser(self.bus)
        self.stream_manager = StreamManager(self.bus)
