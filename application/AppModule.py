#app.py

import time

from core.IngestionModule import IngestionModule
from application.components import StreamManagerInterface, Consumers

udp_cfg = {
    "handshake_timeout_sec": 3.0,
    "device_ip": "192.168.40.12",
    "device_control_port": 5006,
    "device_frame_port": 5005,
    "alive_interval_sec": 1.0,
}


class ApplicationModule:
    """
    Application Layer container for independent services.
    Provides access to the core-layer modules through their interfaces.
    """
    def __init__(self, udp_cfg):

        #  -- Instantiate Core Layer components
        self.ingestion_module = IngestionModule(udp_cfg)
        # TODO: Instantiate ML Processing Layer
        # TODO: Instantiate reference to DBMS

        #  -- Instantiate Application Layer interfaces
        self.stream_interface = StreamManagerInterface(self.ingestion_module.stream_manager)
        # TODO: instantiate clip ingestion service
        # TODO: instantite clip retrieval service
        # TODO: instantiate udp management service
        # TODO: Instantiate Auth Service
 

        # Register consumers for the Ingestion Module
        self.stream_interface.register_consumer(Consumers.ML_LAYER)
        self.stream_interface.register_consumer(Consumers.Streamer)


    def start_stream(self):
        pass
        #self.udp_interface.send_start_stream()


    def stop_stream(self):
        pass
        #self.udp_interface.send_stop_stream()


    def retrieve_a_clip(self):
        pass


    def delete_a_clip(self):
        pass


def main():
    app = ApplicationModule(udp_cfg)
    #app.start_stream()
    #while True:
    #    time.sleep(1)
