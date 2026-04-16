"""
Tubor Web — Schémas Pydantic
"""

from pydantic import BaseModel, field_validator
from typing import Optional
import re


# ── Téléchargements ──────────────────────────────────────────────────────────

class AddDownloadRequest(BaseModel):
    url: str
    format: str       = "video"
    quality: str      = "best"
    output_folder: str = ""
    playlist_mode: str = "single"
    playlist_limit: int = 0
    embed_metadata: bool  = True
    embed_thumbnail: bool = True
    cookies_file: str = ""
    scheduled_at: float = 0.0   # Unix timestamp, 0 = immédiat

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^https?://", v, re.IGNORECASE):
            raise ValueError("URL invalide — doit commencer par http:// ou https://")
        return v


class DownloadItemResponse(BaseModel):
    id: str
    url: str
    format: str
    quality: str
    status: str
    title: str
    filename: str
    filepath: str
    percent: float
    speed: str
    eta: str
    error_message: str
    retry_count: int  = 0
    country_code: str = ""
    country_name: str = ""


class ReorderRequest(BaseModel):
    order: list[str]   # IDs dans le nouvel ordre


# ── Configuration ────────────────────────────────────────────────────────────

class ConfigResponse(BaseModel):
    download_folder: str
    format: str
    quality: str
    theme: str
    embed_metadata: bool
    embed_thumbnail: bool
    playlist_mode: str
    playlist_limit: int
    cookies_file: str
    concurrent_downloads: int
    # Réseau
    proxy_enabled: bool
    proxy: str
    proxy_list: list
    proxy_rotation: bool
    max_retries: int
    sleep_interval: int
    bandwidth_limit: str
    # Planification
    night_mode: bool
    night_start: int
    night_end: int
    # VPN
    vpn_enabled:         bool
    vpn_type:            str
    vpn_countries:       list
    vpn_custom_cmd:      str
    vpn_reconnect_delay: int


class ConfigUpdateRequest(BaseModel):
    download_folder:   Optional[str]  = None
    format:            Optional[str]  = None
    quality:           Optional[str]  = None
    theme:             Optional[str]  = None
    embed_metadata:    Optional[bool] = None
    embed_thumbnail:   Optional[bool] = None
    playlist_mode:     Optional[str]  = None
    playlist_limit:    Optional[int]  = None
    cookies_file:      Optional[str]  = None
    concurrent_downloads: Optional[int] = None
    # Réseau
    proxy_enabled:     Optional[bool] = None
    proxy:             Optional[str]  = None
    proxy_list:        Optional[list] = None
    proxy_rotation:    Optional[bool] = None
    max_retries:       Optional[int]  = None
    sleep_interval:    Optional[int]  = None
    bandwidth_limit:   Optional[str]  = None
    # Planification
    night_mode:        Optional[bool] = None
    night_start:       Optional[int]  = None
    night_end:         Optional[int]  = None
    # VPN
    vpn_enabled:          Optional[bool] = None
    vpn_type:             Optional[str]  = None
    vpn_countries:        Optional[list] = None
    vpn_custom_cmd:       Optional[str]  = None
    vpn_reconnect_delay:  Optional[int]  = None


# ── Système ──────────────────────────────────────────────────────────────────

class SystemInfoResponse(BaseModel):
    ytdlp_version: str
    ffmpeg_available: bool


class UpdateResponse(BaseModel):
    success: bool
    message: str


# ── Prévisualisation ─────────────────────────────────────────────────────────

class FormatInfo(BaseModel):
    format_id:  str
    ext:        str
    resolution: str
    filesize:   int
    vcodec:     str
    acodec:     str
    fps:        Optional[float] = None
    note:       str = ""


class PreviewResponse(BaseModel):
    title:        str
    thumbnail:    str
    duration:     int           # secondes
    duration_str: str           # "1:23:45"
    uploader:     str
    description:  str
    view_count:   int
    upload_date:  str
    webpage_url:  str
    youtube_id:   Optional[str] = None
    embed_url:    Optional[str] = None
    formats:      list[FormatInfo] = []
    is_live:      bool = False


# ── Statistiques ─────────────────────────────────────────────────────────────

class StatsSummaryResponse(BaseModel):
    total_downloads:      int
    successful_downloads: int
    failed_downloads:     int
    today_downloads:      int
    total_size_bytes:     int
    success_rate:         float


class DailyStatResponse(BaseModel):
    day:           str
    count:         int
    size_bytes:    int
    count_success: int = 0
    count_error:   int = 0


class PlatformStatResponse(BaseModel):
    platform: str
    count:    int


class FormatStatResponse(BaseModel):
    format:      str
    quality:     str
    count:       int
    avg_seconds: Optional[float] = None


class HistoryItemResponse(BaseModel):
    id:            str
    url:           str
    title:         str
    format:        str
    quality:       str
    platform:      str
    status:        str
    file_size:     int
    filepath:      str
    error_message: str
    started_at:    float
    finished_at:   float
    country_code:  str = ""
