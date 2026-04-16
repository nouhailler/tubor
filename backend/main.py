"""
Tubor Web — Application FastAPI v0.3
Lance avec : uvicorn main:app --reload --port 8000
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import downloads, config, system, stats, preview
from api.websocket import router as ws_router
from core.downloader import download_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    download_manager.set_loop(asyncio.get_running_loop())
    yield
    download_manager.cancel_all()


app = FastAPI(
    title="Tubor API",
    description="API REST pour Tubor — téléchargeur vidéo/audio basé sur yt-dlp",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(downloads.router)
app.include_router(config.router)
app.include_router(system.router)
app.include_router(stats.router)
app.include_router(preview.router)
app.include_router(ws_router)


@app.get("/")
def root():
    return {"name": "Tubor API", "version": "0.3.0", "status": "running"}
