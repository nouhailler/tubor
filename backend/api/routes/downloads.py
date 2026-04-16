"""
Tubor Web — Routes API : téléchargements
"""

import subprocess
import shutil
from fastapi import APIRouter, HTTPException
from pathlib import Path

from core.downloader import DownloadTask, download_manager, _task_store
from core.config import Config
from models.schemas import AddDownloadRequest, DownloadItemResponse, ReorderRequest

router = APIRouter(prefix="/api/downloads", tags=["downloads"])


def _config() -> Config:
    c = Config(); c.load(); return c


@router.get("", response_model=list[DownloadItemResponse])
def list_downloads():
    return download_manager.get_all()


@router.post("", response_model=DownloadItemResponse, status_code=201)
def add_download(req: AddDownloadRequest):
    cfg = _config()
    output_folder = req.output_folder or cfg.get("download_folder")
    folder = Path(output_folder)
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise HTTPException(status_code=400, detail=f"Dossier de destination invalide : {e}")

    task = DownloadTask(
        url=req.url,
        format_type=req.format,
        quality=req.quality,
        output_folder=str(folder),
        playlist_mode=req.playlist_mode,
        playlist_limit=req.playlist_limit,
        embed_metadata=req.embed_metadata,
        embed_thumbnail=req.embed_thumbnail,
        cookies_file=req.cookies_file or cfg.get("cookies_file", ""),
        scheduled_at=req.scheduled_at,
    )
    _task_store[task.task_id] = task
    return download_manager.add(task).to_dict()


@router.put("/reorder", status_code=204)
def reorder_queue(body: ReorderRequest):
    """Réordonne la file d'attente (drag-and-drop)."""
    download_manager.reorder(body.order)


@router.delete("/{task_id}", status_code=204)
def cancel_download(task_id: str):
    download_manager.cancel(task_id)


@router.delete("", status_code=204)
def cancel_all():
    download_manager.cancel_all()


@router.post("/clear-finished", status_code=204)
def clear_finished():
    download_manager.clear_finished()


@router.post("/{task_id}/open", status_code=204)
def open_file(task_id: str):
    """Ouvre le fichier avec le lecteur par défaut (xdg-open / open)."""
    item = next((i for i in download_manager.get_all() if i["id"] == task_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Téléchargement introuvable.")

    filepath = item.get("filepath", "").strip()
    if not filepath:
        raise HTTPException(status_code=400, detail="Chemin du fichier non disponible.")
    if not Path(filepath).exists():
        raise HTTPException(status_code=404, detail=f"Fichier introuvable : {filepath}")

    if shutil.which("xdg-open"):
        opener = ["xdg-open", filepath]
    elif shutil.which("open"):
        opener = ["open", filepath]
    else:
        raise HTTPException(status_code=501, detail="Aucune commande d'ouverture disponible.")

    try:
        subprocess.Popen(opener, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Impossible d'ouvrir le fichier : {e}")
