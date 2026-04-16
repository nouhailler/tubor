"""
Tubor Web — Routes API : informations système
"""

from fastapi import APIRouter

from core.downloader import is_ffmpeg_available
from core.utils import get_yt_dlp_version, update_yt_dlp
from models.schemas import SystemInfoResponse, UpdateResponse

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("", response_model=SystemInfoResponse)
def system_info():
    """Retourne les informations système (yt-dlp, ffmpeg)."""
    return {
        "ytdlp_version":   get_yt_dlp_version(),
        "ffmpeg_available": is_ffmpeg_available(),
    }


@router.post("/update-ytdlp", response_model=UpdateResponse)
def update_ytdlp():
    """Lance la mise à jour de yt-dlp via pip."""
    success, message = update_yt_dlp()
    return {"success": success, "message": message}
