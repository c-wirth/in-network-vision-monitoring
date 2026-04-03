#application/dependencies.py
import json

from core.IngestionModule.IngestionModuleInterface import IngestionModuleInterface
from core.MLProcessingModule.MLModuleInterface import MLModuleInterface

from application.services.LiveStreamService import LiveStreamService
from application.services.MLStreamService import MLStreamService
from application.services.ClipIngestionService import ClipIngestionService


with open("application/configs/udp_cfg.json", 'r') as cfg:
    udp_cfg = json.load(cfg)


with open("application/configs/ml_cfg.json", 'r') as cfg:
    ml_cfg = json.load(cfg)

# --- Interfaces ---
_ingestion_interface = IngestionModuleInterface(udp_cfg)
_ml_module_interface = MLModuleInterface(ml_cfg)

# Hi Sean we need the Infrastructure Interface
# _infrastructure_module_interface = InfrastructureModuleInterface(infrastructure_cfg)


# --- Services ---
_live_stream_service = LiveStreamService(_ingestion_interface)
_ml_stream_service = MLStreamService(_ingestion_interface, ml_module_interface=_ml_module_interface)
_clip_ingestion_service = ClipIngestionService(_ml_module_interface)
_clip_ingestion_service.start()


_ml_stream_service.start(test=True)

# TODO on ctrl+c we need to gracefully call the stop functions
#_ml_stream_service.stop()

def get_live_stream_service() -> LiveStreamService:
    return _live_stream_service
