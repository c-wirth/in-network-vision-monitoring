#aplication.routers.live_stream.py

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dependencies import get_live_stream_service

router = APIRouter()

class StreamStatusResponse(BaseModel):
    status: str


@router.get("/mjpeg_stream")
def mjpeg_stream(live_stream_service = Depends(get_live_stream_service)):
    """
    Serve a live MJPEG stream of frames in memory.
    Frontend can point an <img> tag here.
    """
    return StreamingResponse(
        live_stream_service.frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.post("/start", response_model=StreamStatusResponse)
def start_stream(live_stream_service = Depends(get_live_stream_service)):
    live_stream_service.start()
    return StreamStatusResponse(status="started")


@router.post("/stop", response_model=StreamStatusResponse)
def stop_stream(live_stream_service = Depends(get_live_stream_service)):
    live_stream_service.stop()
    return StreamStatusResponse(status="stopped")


@router.get("/status", response_model=StreamStatusResponse)
def stream_status(live_stream_service = Depends(get_live_stream_service)):
    status = "running" if live_stream_service._running else "stopped"
    return StreamStatusResponse(status=status)
