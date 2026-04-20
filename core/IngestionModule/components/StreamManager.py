import threading
from .IngestionEventBus import BusEvents


class StreamManager:
    def __init__(self, bus, max_frames=128):
        self.max_frames = max_frames
        self._buffer = [None] * self.max_frames
        self._consumer_cursors = {}  # consumer_name -> read_seq
        self._lock = threading.Lock()
        self.bus = bus
        self.bus.subscribe(BusEvents.FRAME_READY, self._handle_new_frame)

        # Monotonic write sequence
        self._write_seq = 0

        # Debug state
        self._debug = {
            "writes": 0,
            "polls": 0,
            "misses": 0,
            "overwrites": 0,
            "last_frame_id": None,
            "last_seq": -1,
            "last_delivered": {}
        }
        self._debug_log_every = 100

    def empty_stream_buffer(self):
        with self._lock:
            self._buffer = [None] * self.max_frames
            self._write_seq = 0
            for k in self._consumer_cursors:
                self._consumer_cursors[k] = 0

    def register_consumer(self, name):
        with self._lock:
            self._consumer_cursors[name] = self._write_seq

    def unregister_consumer(self, name):
        with self._lock:
            self._consumer_cursors.pop(name, None)

    def _handle_new_frame(self, data):
        frame_id = data["frame_id"]
        frame = data["frame"]
        self._push_frame(frame_id, frame)

    def _push_frame(self, frame_id, frame):
        with self._lock:
            idx = self._write_seq % self.max_frames

            # Detect overwrite
            existing = self._buffer[idx]
            if existing is not None:
                self._debug["overwrites"] += 1

            self._buffer[idx] = {
                "frame_id": frame_id,
                "frame": frame,
                "seq": self._write_seq
            }

            # Monotonicity check
            if (
                self._debug["last_frame_id"] is not None and
                frame_id <= self._debug["last_frame_id"]
            ):
                print(f"[WARN] non-monotonic frame_id: prev={self._debug['last_frame_id']} curr={frame_id}")

            self._debug["last_frame_id"] = frame_id
            self._debug["last_seq"] = self._write_seq

            self._write_seq += 1
            self._debug["writes"] += 1

            if self._debug["writes"] % self._debug_log_every == 0:
                print(
                    f"[SM WRITE] writes={self._debug['writes']} "
                    f"seq={self._write_seq} idx={idx} frame_id={frame_id} "
                    f"overwrites={self._debug['overwrites']}"
                )

    def poll_frame(self, consumer_name):
        with self._lock:
            read_seq = self._consumer_cursors.get(consumer_name)

            if read_seq is None:
                print(f"[SM POLL] unknown consumer={consumer_name}")
                return None, None

            # No new frames
            if read_seq >= self._write_seq:
                self._debug["misses"] += 1
                return None, None

            # Consumer fell behind
            if self._write_seq - read_seq > self.max_frames:
                new_read_seq = self._write_seq - self.max_frames
                print(
                    f"[SM LAG] consumer={consumer_name} lagged. "
                    f"read_seq={read_seq} -> {new_read_seq} write_seq={self._write_seq}"
                )
                read_seq = new_read_seq

            idx = read_seq % self.max_frames
            slot = self._buffer[idx]

            if slot is None:
                print(
                    f"[SM NULL] consumer={consumer_name} idx={idx} "
                    f"read_seq={read_seq} write_seq={self._write_seq}"
                )
                self._debug["misses"] += 1
                return None, None

            # Consistency check
            if slot["seq"] != read_seq:
                print(
                    f"[SM MISMATCH] consumer={consumer_name} "
                    f"expected_seq={read_seq} actual_seq={slot['seq']} idx={idx}"
                )

            # Detect stuck frame
            last = self._debug["last_delivered"].get(consumer_name)
            curr = slot["frame_id"]
            if last == curr:
                print(f"[SM STUCK] consumer={consumer_name} frame_id={curr}")
            self._debug["last_delivered"][consumer_name] = curr

            self._consumer_cursors[consumer_name] = read_seq + 1
            self._debug["polls"] += 1

            if self._debug["polls"] % self._debug_log_every == 0:
                print(
                    f"[SM POLL] polls={self._debug['polls']} "
                    f"consumer={consumer_name} seq={read_seq} idx={idx} "
                    f"frame_id={curr} write_seq={self._write_seq}"
                )

            return curr, slot["frame"]

    def debug_heartbeat(self):
        with self._lock:
            print(
                f"[SM HEARTBEAT] write_seq={self._write_seq} "
                f"consumers={len(self._consumer_cursors)} "
                f"writes={self._debug['writes']} polls={self._debug['polls']} "
                f"misses={self._debug['misses']} overwrites={self._debug['overwrites']}"
            )
