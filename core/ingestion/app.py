#app.py

import sleep

from UDPManager import UDPManager
from FrameParser import FrameParser
from StreamManager import StreamManager



udp_cfg = {
    "handshake_timeout_sec": 3.0,
    "device_ip": "192.168.40.12",
    "device_control_port": 5006,
    "device_frame_port": 5005,
    "alive_interval_sec": 1.0,
}



def main():

    bus = EventBus()

    udp_manager = UDPManager(udp_cfg, bus)

    frame_parser = FrameParser(bus)

    stream_manager = StreamManager()

    while True:
        time.sleep(1)
