# core.MLProcessingModule.componets.FrameReceiver


from .MLEventBus import EventBus, BusEvents

class FrameReceiver:

    def __init__(self, internal_frame_buffer_sz , bus: EventBus):

        self.buffer_size = internal_frame_buffer_sz
        self.frame_buffer = [None] * self.buffer_size
        self.write_idx = 0 # this is a refernce to the last written position in the frame_buffer
        self.bus = bus

        self.bus.subscribe(BusEvents.ON_DETECTION, self._on_detection)


    def receive(self, frame_bytes):
            """
            Inserts frame into ring buffer.
            When write_idx wraps to 0, trigger detection event
            """

            # write frame
            self.frame_buffer[self.write_idx] = frame_bytes

            # advance pointer and wrap
            self.write_idx = (self.write_idx + 1) % self.buffer_size

            if self.write_idx == 0:
                self.bus.publish(BusEvents.PUSH_FRAME_TO_ML_MODULE, self.frame_buffer[0])

    def _on_detection(self):
        snapshot = list(self.frame_buffer)
        self.bus.publish(BusEvents.PUSH_SNAPSHOT_TO_BUILDER, snapshot)
