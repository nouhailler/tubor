"""
Tubor Web — Route API : prévisualisation avant téléchargement
Utilise yt-dlp --dump-json pour extraire les métadonnées sans télécharger.
"""

import json
import re
import subprocess
from fastapi import APIRouter, HTTPException, Query

from core.downloader import _ytdlp_executable, _normalize_proxy
from core.config import Config
from models.schemas import PreviewResponse, FormatInfo

router = APIRouter(prefix="/api/preview", tags=["preview"])


def _youtube_id(url: str) -> str | None:
    m = re.search(
        r"(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})",
        url
    )
    return m.group(1) if m else None


def _fmt_duration(seconds: int) -> str:
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _human_size(b: int) -> str:
    if b <= 0:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.0f} {unit}"
        b //= 1024
    return f"{b} GB"


@router.get("", response_model=PreviewResponse)
def get_preview(url: str = Query(..., description="URL de la vidéo à prévisualiser")):
    """
    Extrait les métadonnées d'une URL sans télécharger le contenu.
    Temps de réponse typique : 2-8 secondes.
    """
    cfg = Config()

    cmd = [
        *_ytdlp_executable(),
        "--dump-json",
        "--no-playlist",
        "--no-warnings",
        "--socket-timeout", "20",
    ]

    proxy = _normalize_proxy(cfg.get("proxy", ""))
    if proxy:
        cmd += ["--proxy", proxy]

    cmd.append(url.strip())

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Délai d'attente dépassé pour récupérer les métadonnées.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()[:300]
        raise HTTPException(status_code=400, detail=err or "yt-dlp n'a pas pu récupérer les métadonnées.")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Réponse yt-dlp invalide (JSON malformé).")

    # ── Formats ──────────────────────────────────────────────────────────────
    formats: list[FormatInfo] = []
    seen_res: set[str] = set()

    for f in reversed(data.get("formats", [])):   # reversed = meilleure qualité en premier
        ext = f.get("ext", "")
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")

        # Ignorer les formats audio-seulement ou vidéo-seulement dans la liste affichée
        # (on garde les formats combinés + les formats vidéo connus)
        height = f.get("height")
        if not height and vcodec == "none":
            continue

        res = f.get("resolution") or (f"{height}p" if height else "audio")
        if res in seen_res:
            continue
        seen_res.add(res)

        filesize = f.get("filesize") or f.get("filesize_approx") or 0
        formats.append(FormatInfo(
            format_id=str(f.get("format_id", "")),
            ext=ext,
            resolution=res,
            filesize=filesize,
            vcodec=vcodec if vcodec != "none" else "",
            acodec=acodec if acodec != "none" else "",
            fps=f.get("fps"),
            note=_human_size(filesize),
        ))

        if len(formats) >= 12:
            break

    # ── YouTube embed ─────────────────────────────────────────────────────────
    yt_id    = _youtube_id(url)
    embed_url = (
        f"https://www.youtube-nocookie.com/embed/{yt_id}?autoplay=1&end=30"
        if yt_id else None
    )

    duration = int(data.get("duration") or 0)

    return PreviewResponse(
        title        = data.get("title", ""),
        thumbnail    = data.get("thumbnail", ""),
        duration     = duration,
        duration_str = _fmt_duration(duration),
        uploader     = data.get("uploader") or data.get("channel") or "",
        description  = (data.get("description") or "")[:400],
        view_count   = data.get("view_count") or 0,
        upload_date  = data.get("upload_date") or "",
        webpage_url  = data.get("webpage_url") or url,
        youtube_id   = yt_id,
        embed_url    = embed_url,
        formats      = formats,
        is_live      = bool(data.get("is_live")),
    )
