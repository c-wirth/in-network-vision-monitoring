#UDPManager.py
import socket
import time
import threading
import os
from PIL import Image
import io
import struct

from .IngestionEventBus import BusEvents

FLAG_HANDSHAKE      = 0x0001
FLAG_HANDSHAKE_ACK  = 0x0002
FLAG_STOP_STREAM    = 0x0003
FLAG_START_STREAM   = 0x0004
FLAG_PACKET_LOSS    = 0x0005
FLAG_ALIVE          = 0x0006

HEADER_SIZE = 8


class UDPManager:

    def __init__(self, cfg, bus, simulate_stream=False):
        self.bus = bus
        self.cfg = cfg
        self.is_running = False
        self.is_streaming = False

        self.simulate_stream = cfg.get("simulate_stream", False)
        self.simulation_dir = cfg.get("simulation_dir", None)
        self.simulation_interval = cfg.get("simulation_interval", 0.01)

        self._stream_thread = None

        if not self.simulate_stream:
            self._establish_connection()

        else:
            print("[WARNING] stream started UDPManager started with simulate_stream=True")

        self.bus.subscribe(BusEvents.CONTROL_SIGNAL, self._handle_incoming_command)

    def _establish_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.cfg["device_frame_port"]))
        self.sock.settimeout(self.cfg["handshake_timeout_sec"])

        # flush the buffer
        self.sock.setblocking(False)
        while True:
            try:
                self.sock.recvfrom(1400)
            except BlockingIOError:
                break
        self.sock.setblocking(True)

        # handshake
        print("Beginning handshake...")
        start_time = time.time()
        while True:
            if time.time() - start_time > self.cfg["handshake_timeout_sec"]:
                raise TimeoutError("Handshake timed out")
            try:
                data, addr = self.sock.recvfrom(1400)
                if len(data) < HEADER_SIZE:
                    continue

                try:
                    flags = struct.unpack('>H', data[6:8])[0]
                except struct.error as e:
                    print(f"ERROR: failed to unpack header: {e}")
                    continue

                if flags == FLAG_HANDSHAKE:
                    print(f"Handshake received from {addr} — sending ACK")
                    ack = self._make_packet(FLAG_HANDSHAKE_ACK)
                    self.sock.sendto(ack, (self.cfg["device_ip"], self.cfg["device_control_port"]))
                    self.is_running = True
                    break
                else:
                    print(
                        f"ERROR: received unexpected flag from sensor. "
                        f"Received {flags}, expected FLAG_HANDSHAKE"
                    )

            except socket.timeout:
                continue


    def _make_packet(self, flags, payload=b''):
        header = struct.pack('>HHHH', 0, 0, 0, flags)
        return header + payload


    def send_control(self, flags, payload=b''):
        self.sock.sendto(self._make_packet(flags, payload),
                         (self.cfg["device_ip"], self.cfg["device_control_port"]))


    def _start_receiving(self):
        """
        Main receive loop for packets from the edge device.
        Publishes frame fragments or messages to the bus.
        """
        if not self.is_running:
            print("[UDP WARNING] UDPManager is not running. Cannot start receive loop.")
            return

        self.sock.settimeout(0.01)
        print("[UDP DEBUG] UDPManager receive loop started.")

        try:
            while self.is_running:
                try:
                    data, addr = self.sock.recvfrom(1400)
                except socket.timeout:
                    time.sleep(0.001)
                    continue

                if len(data) < HEADER_SIZE:
                    continue  # ignore incomplete packets

                # unpack header
                try:
                    frame_id, frag_id, total_frags, flags = struct.unpack(">HHHH", data[:HEADER_SIZE])
                except struct.error as e:
                    print(f"ERROR: failed to unpack header: {e}")
                    continue

                payload = data[HEADER_SIZE:]

                self.bus.publish(BusEvents.FRAME_RECEIVED, {
                    "frame_id": frame_id,
                    "frag_id": frag_id,
                    "total_frags": total_frags,
                    "payload": payload
                })

        except KeyboardInterrupt:
            print("Receive loop interrupted by user.")
        finally:
            print("UDPManager receive loop exiting.")


    def _handle_incoming_command(self, cmd):
        """
        Handles commands from the Application Layer via the bus.
        START_STREAM/STOP_STREAM either triggers UDP or simulation.
        """
        action = cmd.get("action")

        if action == "start_stream":
            if self.is_streaming:
                print("[UDPManager WARNING] Stream already streaming, returning...")
                return

            self.is_streaming = True

            if self.simulate_stream:
                print("[UDPManager DEBUG] Starting simulated stream...")
                self._stream_thread = threading.Thread(target=self._simulate_stream, daemon=True)
            else:
                print("[UDPManager DEBUG] Starting real UDP stream...")
                self.send_control(FLAG_START_STREAM)
                self._stream_thread = threading.Thread(target=self._start_receiving, daemon=True)

            self._stream_thread.start()
            self.bus.publish(BusEvents.START_STREAM)

        elif action == "stop_stream":
            if not self.is_running:
                print("[UDPManager DEBUG] Stream not running")
                return

            print("[UDPManager DEBUG] Stopping stream...")
            self.is_running = False
            if not self.simulate_stream:
                self.send_control(FLAG_STOP_STREAM)

            if self._stream_thread and self._stream_thread.is_alive():
                self._stream_thread.join(timeout=1.0)
            self.bus.publish(BusEvents.STOP_STREAM)
            print("[UDPManager DEBUG] Stream stopped")

        else:
            print(f"[UDPManager DEBUG] UNKNOWN action received by UDPManager: {action}")


    def compress_frame(self, frame_bytes: bytes) -> bytes:
        """Re-encode JPEG frames to simulate compression."""
        with Image.open(io.BytesIO(frame_bytes)) as img:
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            return buf.getvalue()


    def _simulate_stream(self):
        """Publish frames sequentially from a folder, preserving order with a simple counter as frame_id."""
        if not self.simulation_dir or not os.path.exists(self.simulation_dir):
            print("Simulation directory invalid")
            return

        files = sorted(os.listdir(self.simulation_dir))
        if not files:
            print("No frames found in simulation directory")
            return

        frame_id = 0  # sequential ID independent of filename

        for fname in files:
            if not self.is_running:
                print("Simulation stopped before completing all frames")
                return  # stop gracefully

            path = os.path.join(self.simulation_dir, fname)
            with open(path, "rb") as f:
                frame_bytes = f.read()

            compressed_frame = self.compress_frame(frame_bytes)

            self.bus.publish(BusEvents.FRAME_READY, {
                "frame_id": frame_id,
                "frame": compressed_frame
            })

            #print(f"[DEBUG UDPManager] Published frame_id={frame_id}, file={fname}")

            frame_id += 1
            time.sleep(self.simulation_interval)

        print("Simulation finished: all frames published")
        self.is_running = False
        self.bus.publish(BusEvents.STOP_STREAM)
