#app.py

import time

from application.components.Consumers import Consumers
from application.interfaces.IngestionModuleInterface import IngestionModuleInterface 
from application.services.StreamService import StreamService

udp_cfg = {
    "handshake_timeout_sec": 3.0,
    "device_ip": "192.168.40.12",
    "device_control_port": 5006,
    "device_frame_port": 5005,
    "alive_interval_sec": 1.0,


   "simulate_stream": True,
   "simulation_dir": "/Users/colby/Desktop/sim_clip/",
   "simulation_interval": 0.01
}


class ApplicationModule:
    """
    Application Layer container for independent services.
    Provides access to the core-layer modules through their interfaces.
    """
    def __init__(self, udp_cfg):


        #  -- Instantiate Application Layer interfaces
        self.ingestion_interface = IngestionModuleInterface(udp_cfg)
        # TODO: instantiate clip ingestion service
        # TODO: instantite clip retrieval service
        # TODO: Instantiate Auth Service


        # -- Instantiate Services
        self.stream_service = StreamService(self.ingestion_interface)
 


    def start_stream(self):
        self.ingestion_interface.start_stream()
        self.stream_service.start()


    def stop_stream(self):
        self.ingestion_interface.stop_stream()
        self.stream_service.stop()


    def start_detection_service(self):
        pass


    def stop_detection_service(self):
        pass


    def retrieve_a_clip(self):
        pass


    def delete_a_clip(self):
        pass


def main():
    print("Beginning 10 second stream test.")
    app = ApplicationModule(udp_cfg)
    app.start_stream()
    time.sleep(20)
    app.stop_stream()


if __name__ == "__main__":
    main()
