# core.MLProcessingModule.componets.FrameReceiver


from .MLEventBus import EventBus, BusEvents
from collections import deque

class FrameReceiver:

    def __init__(self, internal_frame_buffer_sz , bus: EventBus):

        self.stream_thread = None
        self.frame_buffer = deque(maxlen=internal_frame_buffer_sz)
        self.bus = bus
        self.bus.subscribe(BusEvents.FRAME_RECEIVED, self.handle_incoming_frame)


    def receive(self, frame_bytes):
        '''
        polls a frame and puts it to the internal frame buffer, converts to np array first for compression

        if a frame is put into the first idx (idx 0) of the buffer, it is immediately pushed to the detection_buffer bus where it will override the old frame
        '''


