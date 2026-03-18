# StreamManagerInterface.py

from application.components import Consumers

class StreamManagerInterface:
    """
    Provides a clean API to consumers (ML layer, streamers) to access frames
    from the IngestionModule's StreamManager. The interface handles
    consumer registration and frame polling, abstracting the underlying buffer.
    """

    def __init__(self, stream_manager):
        self._stream_manager = stream_manager

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
