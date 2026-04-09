import json
from core.IngestionModule.IngestionModuleInterface import IngestionModuleInterface
from core.MLProcessingModule.MLModuleInterface import MLModuleInterface
from application.services.LiveStreamService import LiveStreamService
from application.services.MLStreamService import MLStreamService
from application.services.ClipIngestionService import ClipIngestionService
from core.db_infrastructure.db_interface import DBInterface
from application.services.user_auth_service import AuthService
from application.services.notification_service import NotificationService


# Load configs
with open("application/configs/udp_cfg.json", 'r') as cfg:
    udp_cfg = json.load(cfg)

with open("application/configs/ml_cfg.json", 'r') as cfg:
    ml_cfg = json.load(cfg)

# Interfaces
_ingestion_interface = IngestionModuleInterface(udp_cfg)
_ml_module_interface = MLModuleInterface(ml_cfg)
_db_interface = DBInterface()
_auth_service = AuthService(_db_interface)
_notification_service = NotificationService()

# Hi Sean we need the Infrastructure Interface
# _infrastructure_module_interface = InfrastructureModuleInterface(infrastructure_cfg)

# Service instances
_live_stream_service = LiveStreamService(_ingestion_interface)
_ml_stream_service = MLStreamService(_ingestion_interface, ml_module_interface=_ml_module_interface)
_clip_ingestion_service = ClipIngestionService(
    _ml_module_interface,
    db_interface=_db_interface,
    notification_service=_notification_service
)


# Hi Sean we also need the Auth and Notification services
# _auth_service = UserAuthService(_infrastructure_module_interface)
# _notification_service = NotificationService(_infrastructure_module_interface)

# Accessors
def get_live_stream_service(): return _live_stream_service
def get_ml_stream_service(): return _ml_stream_service
def get_clip_ingestion_service(): return _clip_ingestion_service
def get_auth_service(): return _auth_service
