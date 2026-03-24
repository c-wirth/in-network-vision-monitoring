#app.py

import time

from core.IngestionModule import IngestionModule
from application.components import, IngestionModuleInterface Consumers

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


        #  -- Instantiate Application Layer interfaces
        self.ingestion_interface = IngestionModuleInterface(self.ingestion_module.stream_manager)
        # TODO: instantiate clip ingestion service
        # TODO: instantite clip retrieval service
        # TODO: Instantiate Auth Service
 

        # Register consumers for the Ingestion Module
        self.ingestion_interface.register_consumer(Consumers.ML_LAYER)
        self.ingestion_interface.register_consumer(Consumers.Streamer)


    def start_stream(self):
        self.ingestion_module.start_stream()


    def stop_stream(self):
        pass
        self.ingestion_module.stop_stream()


    def start_detection_service(self):
        pass


    def stop_detection_service(self):
        pass


    def retrieve_a_clip(self):
        pass


    def delete_a_clip(self):
        pass


def main():
    app = ApplicationModule(udp_cfg)
    app.start_stream()
    while True:

        time.sleep(1)
