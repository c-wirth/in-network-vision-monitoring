# IngestionModuleInferface.py
from .components import EventBus, BusEvents, UDPManager, FrameParser, StreamManager

class IngestionModuleInterface:
    def __init__(self, udp_cfg):

        self.bus = EventBus()
        self.udp_manager = UDPManager(udp_cfg, self.bus)
        self.frame_parser = FrameParser(self.bus)
        self._stream_manager = StreamManager(self.bus)


    def register_consumer(self, consumer: "Consumer"):
        """
        Register a new consumer to start receiving frames.
        """
        self._stream_manager.register_consumer(consumer.name)


    def unregister_consumer(self, consumer: "Consumer"):
        """
        Unregister a consumer to stop receiving frames.
        """
        self._stream_manager.unregister_consumer(consumer.name)


    def poll_frame(self, consumer: "Consumer"):
        """
        Poll the next available frame for a given consumer.
        Returns (frame_id, frame) or (None, None) if no new frame.
        """
        return self._stream_manager.poll_frame(consumer.name)


    def start_stream(self):
        """
        Sends the signal to the UDP layer to start video stream
        """
        self.bus.publish(BusEvents.CONTROL_SIGNAL, {
            "action": "start_stream"
        })


    def stop_stream(self):
        """
        Sends the signal to the UDP layer to stop video stream
        """
        self.bus.publish(BusEvents.CONTROL_SIGNAL, {
            "action": "stop_stream"
        })
