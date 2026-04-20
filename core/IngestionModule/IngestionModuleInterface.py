# core/IngestionModule/IngestionModuleInterface.py
from .components import EventBus, BusEvents, UDPManager, FrameParser, StreamManager

class IngestionModuleInterface:
    def __init__(self, udp_cfg):

        self.bus = EventBus()
        self.udp_manager = UDPManager(udp_cfg, self.bus)
        self.frame_parser = FrameParser(self.bus)
        self._stream_manager = StreamManager(self.bus)

    def get_udp_running_status(self):
        print(f"[DEBUG] UDP_MANAGER running status: {self.udp_manager.is_running}")
        return self.udp_manager.is_running

    def get_udp_streaming_status(self):
        print(f"[DEBUG] UDP_MANAGER streaming status: {self.udp_manager.is_streaming}")
        return self.udp_manager.is_streaming

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
        print("[IngestionModuleInterface DEBUG] sending start_stream_signal")
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
        self._stream_manager.empty_stream_buffer()
