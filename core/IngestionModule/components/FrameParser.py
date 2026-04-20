# FrameParser.py
import threading
import time
from collections import defaultdict
from .IngestionEventBus import BusEvents

class FrameParser:
    def __init__(self, bus, fragment_timeout_sec=5.0):
        self.bus = bus
        self.fragment_timeout_sec = fragment_timeout_sec
        self.bus.subscribe(BusEvents.FRAME_RECEIVED, self._handle_fragment)

        self._fragments: dict[int, dict[int, bytes]] = defaultdict(dict)
        self._total_frags: dict[int, int] = {}
        self._timestamps: dict[int, float] = {}
        self._lock = threading.Lock()

        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def _handle_fragment(self, data):
        frame_id    = data["frame_id"]
        frag_id     = data["frag_id"]
        total_frags = data["total_frags"]
        payload     = data["payload"]

        completed_frame = None  # will hold (frame_id, frame_bytes) if ready

        with self._lock:
            # Validate total_frags consistency
            if frame_id in self._total_frags:
                if self._total_frags[frame_id] != total_frags:
                    print(f"[FrameParser] WARNING: inconsistent total_frags for frame {frame_id} "
                          f"(expected {self._total_frags[frame_id]}, got {total_frags}). Dropping.")
                    self._discard_frame(frame_id)
                    return
            else:
                self._total_frags[frame_id] = total_frags
                self._timestamps[frame_id] = time.monotonic()

            self._fragments[frame_id][frag_id] = payload

            if len(self._fragments[frame_id]) == total_frags:
                expected_ids = set(range(total_frags))
                received_ids = set(self._fragments[frame_id].keys())

                if expected_ids != received_ids:
                    print(f"[FrameParser] Fragment ID mismatch for frame {frame_id}. "
                          f"Missing: {expected_ids - received_ids}. Dropping.")
                    self._discard_frame(frame_id)
                    return

                frame_bytes = b''.join(
                    self._fragments[frame_id][i] for i in range(total_frags)
                )
                completed_frame = (frame_id, frame_bytes)
                self._discard_frame(frame_id)
            # else: still accumulating, do nothing

        # ---- Publish OUTSIDE the lock ----
        if completed_frame is not None:
            fid, fbytes = completed_frame
            self.bus.publish(BusEvents.FRAME_READY, {"frame_id": fid, "frame": fbytes})

    def _discard_frame(self, frame_id):
        """Remove all state for a frame. Must be called under self._lock."""
        self._fragments.pop(frame_id, None)
        self._total_frags.pop(frame_id, None)
        self._timestamps.pop(frame_id, None)

    def _cleanup_loop(self):
        """Evict frames whose fragments never fully arrived."""
        while True:
            time.sleep(self.fragment_timeout_sec / 2)
            now = time.monotonic()
            with self._lock:
                stale = [
                    fid for fid, ts in self._timestamps.items()
                    if now - ts > self.fragment_timeout_sec
                ]
                for fid in stale:
                    received = len(self._fragments.get(fid, {}))
                    expected = self._total_frags.get(fid, "?")
                    print(f"[FrameParser] Timeout: evicting stale frame {fid} "
                          f"({received}/{expected} fragments)")
                    self._discard_frame(fid)
