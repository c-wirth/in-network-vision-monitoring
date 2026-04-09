# application/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routers import auth
from core.db_infrastructure.db_components.connections import init_db

# Import routers
from .routers import live_stream, notifications_and_clip_view

# Import service instances from dependencies
from .dependencies import (
    get_live_stream_service,
    get_ml_stream_service,
    get_clip_ingestion_service
)

# Get service instances
live_stream_service = get_live_stream_service()
ml_stream_service = get_ml_stream_service()
clip_ingestion_service = get_clip_ingestion_service()



TEST_ML_SERVICE = False

# ---------------- Lifespan context ----------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start services on startup, stop on shutdown."""
    # Startup
    init_db()
    clip_ingestion_service.start()
    ml_stream_service.start(test=TEST_ML_SERVICE)
    print("[main] Services started.")
    try:
        yield  # Control passes to FastAPI
    finally:
        # Shutdown
        ml_stream_service.stop()
        clip_ingestion_service.stop()
        print("[main] Services stopped.")


# ---------------- FastAPI app ----------------
app = FastAPI(title="AI-Enabled In Network Monitoring", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(live_stream.router, prefix="/stream", tags=["Live Stream"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(notifications_and_clip_view.router, prefix="/clips", tags=["Clips"])

# ---------------- Main entry point ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("application.main:app", host="0.0.0.0", port=8000, reload=False)

# uvicorn application.main:app --reload
# http://127.0.0.1:8000/docs