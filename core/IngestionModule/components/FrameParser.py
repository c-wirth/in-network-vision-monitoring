# FrameParser.py
import threading
from collections import defaultdict
from EventBus import EventBus, BusEvents

class FrameParser:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.bus.subscribe(BusEvents.FRAME_RECEIVED, self._handle_fragment)

        # Internal storage for reassembling frames
        self._fragments = defaultdict(dict)  # frame_id -> {frag_id: payload}
        self._total_frags = {}               # frame_id -> total fragments

        self._lock = threading.Lock()

    def _handle_fragment(self, data):
        """
        Called by the bus when UDPManager publishes a frame fragment.
        """
        frame_id    = data["frame_id"]
        frag_id     = data["frag_id"]
        total_frags = data["total_frags"]
        payload     = data["payload"]

        with self._lock:
            self._fragments[frame_id][frag_id] = payload
            self._total_frags[frame_id] = total_frags

            # Check if all fragments are received
            if len(self._fragments[frame_id]) == total_frags:
                frame_bytes = b''.join(
                    self._fragments[frame_id][i] for i in range(total_frags)
                )

                # Publish full frame to downstream (StreamManager)
                self.bus.publish(BusEvents.FRAME_READY, {"frame_id": frame_id, "frame": frame_bytes})

                del self._fragments[frame_id]
                del self._total_frags[frame_id]

            else:
                print(f"Fragment Frame received in FrameParser with frame id: {frame_id}")
