"""
Tubor - Gestionnaire de configuration persistante
Stockage dans ~/.config/tubor/config.json
"""

import json
import os
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "tubor"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS = {
    "download_folder": str(Path.home() / "Downloads"),
    "format": "video",          # "video" | "audio"
    "quality": "best",          # "best" | "1080p" | "720p" | "480p" | "360p" | "mp3_320" | "mp3_192" | "mp3_128"
    "theme": "dark",            # "dark" | "light"
    "embed_metadata": True,
    "embed_thumbnail": True,
    "playlist_mode": "single",  # "single" | "all"
    "playlist_limit": 0,        # 0 = illimité
    "cookies_file": "",
    "username": "",
    "concurrent_downloads": 1,
    "window_geometry": None,
    "show_log": True,
}


class Config:
    """Gestionnaire de configuration de Tubor."""

    def __init__(self):
        self._data: dict = {}
        self._ensure_dir()
        self.load()

    def _ensure_dir(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def load(self):
        """Charge la configuration depuis le fichier JSON."""
        self._data = dict(DEFAULTS)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self._data.update(saved)
            except (json.JSONDecodeError, OSError):
                pass  # Utilise les valeurs par défaut en cas d'erreur

    def save(self):
        """Sauvegarde la configuration dans le fichier JSON."""
        self._ensure_dir()
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"[Config] Erreur de sauvegarde : {e}")

    def get(self, key: str, fallback=None):
        return self._data.get(key, DEFAULTS.get(key, fallback))

    def set(self, key: str, value):
        self._data[key] = value

    def update(self, data: dict):
        self._data.update(data)

    def __getitem__(self, key):
        return self._data.get(key, DEFAULTS.get(key))

    def __setitem__(self, key, value):
        self._data[key] = value

    @property
    def download_folder(self) -> str:
        return self._data.get("download_folder", DEFAULTS["download_folder"])

    @property
    def format(self) -> str:
        return self._data.get("format", DEFAULTS["format"])

    @property
    def quality(self) -> str:
        return self._data.get("quality", DEFAULTS["quality"])

    @property
    def theme(self) -> str:
        return self._data.get("theme", DEFAULTS["theme"])

    @property
    def embed_metadata(self) -> bool:
        return self._data.get("embed_metadata", DEFAULTS["embed_metadata"])

    @property
    def embed_thumbnail(self) -> bool:
        return self._data.get("embed_thumbnail", DEFAULTS["embed_thumbnail"])
