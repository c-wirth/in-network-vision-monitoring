#application/dependencies.py
import json

from core.IngestionModule.IngestionModuleInterface import IngestionModuleInterface


from application.services.LiveStreamService import LiveStreamService
from application.services.MLStreamService import MLStreamService


with open("configs/udp_cfg.json", 'r') as cfg:
    udp_cfg = json.load(cfg)


with open("configs/ml_cfg.json", 'r') as cfg:
    ml_cfg = json.load(cfg)

_ingestion_interface = IngestionModuleInterface(udp_cfg)
_live_stream_service = LiveStreamService(_ingestion_interface)

# TODO implement this
# _ml_module_interface = MLModuleInterface(ml_cfg)
# _ml_stream_service = MLStreamService(_ingestion_interface, ml_module_interface=ml_module_interface)
# _ml_stream_service.start()

# on shutdown
# _ml_stream_service.stop()

def get_live_stream_service() -> LiveStreamService:
    return _live_stream_service
