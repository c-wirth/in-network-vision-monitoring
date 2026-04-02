# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the singleton instances from dependencies
from routers import live_stream

app = FastAPI(title="AI-Enabled In Network Monitoring")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(live_stream.router, prefix="/stream", tags=["Live Stream"])

# ---------------- Main entry point ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
