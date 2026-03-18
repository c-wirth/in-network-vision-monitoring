#UDPManager.py
import socket
import time

from EventBus import BusEvents

FLAG_HANDSHAKE      = 0x0001
FLAG_HANDSHAKE_ACK  = 0x0002
FLAG_STOP_STREAM    = 0x0003
FLAG_START_STREAM   = 0x0004
FLAG_PACKET_LOSS    = 0x0005
FLAG_ALIVE          = 0x0006

HEADER_SIZE = 8


class UDPManager:

    def __init__(self, cfg, bus: EventBus):
        self.bus = bus
        self.cfg = cfg
        self.is_running = False
        self._establish_connection()

        self.bus.subscribe(BusEvents.CONTROL_SIGNAL, self._handle_incoming_command) # incoming signals from application layer


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
            print("UDPManager is not running. Cannot start receive loop.")
            return

        self.sock.settimeout(0.01)
        print("UDPManager receive loop started.")

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
        Only START_STREAM and STOP_STREAM go to the edge device.
        SHUTDOWN only stops this ingestion layer.
        """
        action = cmd.get("action")

        if action == "start_stream":
            if not self.is_running:
                self.send_control(FLAG_START_STREAM)
                self.is_running = True
                self._start_receiving()
                self.bus.publish(BusEvents.START_STREAM)  # notify FrameParser / StreamManager

        elif action == "stop_stream":
            if self.is_running:
                self.send_control(FLAG_STOP_STREAM)
                self.is_running = False
                self.bus.publish(BusEvents.STOP_STREAM)  # notify FrameParser / StreamManager

        else:
            print(f"UNKNOWN action received by the UDPManager: received {action}")
