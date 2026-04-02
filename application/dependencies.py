import json

from core.IngestionModule.IngestionModuleInterface import IngestionModuleInterface
from application.services.LiveStreamService import LiveStreamService


with open("cfg.json", 'r') as cfg:
    udp_cfg = json.load(cfg)

_ingestion_interface = IngestionModuleInterface(udp_cfg)

_live_stream_service = LiveStreamService(_ingestion_interface)

def get_live_stream_service() -> LiveStreamService:
    return _live_stream_service
