"""
Tubor - Utilitaires divers
"""

import re
import subprocess
import sys
from pathlib import Path


def is_valid_url(url: str) -> bool:
    """Vérifie si une chaîne ressemble à une URL valide."""
    url = url.strip()
    pattern = re.compile(
        r'^(https?://)'
        r'[\w\-]+(\.[\w\-]+)+'
        r'.*$',
        re.IGNORECASE
    )
    return bool(pattern.match(url))


def get_yt_dlp_version() -> str:
    """Retourne la version de yt-dlp installée."""
    try:
        import yt_dlp
        return yt_dlp.version.__version__
    except Exception:
        return "?"


def update_yt_dlp() -> tuple[bool, str]:
    """Tente de mettre à jour yt-dlp via pip. Retourne (succès, message)."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp",
             "--break-system-packages"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            new_version = get_yt_dlp_version()
            return True, f"yt-dlp mis à jour avec succès → {new_version}"
        else:
            return False, result.stderr.strip() or "Échec de la mise à jour."
    except subprocess.TimeoutExpired:
        return False, "La mise à jour a pris trop de temps."
    except Exception as e:
        return False, str(e)


def send_desktop_notification(title: str, body: str, urgency: str = "normal"):
    """Envoie une notification bureau via notify-send si disponible."""
    import shutil
    if shutil.which("notify-send"):
        try:
            subprocess.Popen(
                ["notify-send", "-u", urgency, "-i", "folder-download", title, body],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            pass


def sanitize_filename(name: str) -> str:
    """Nettoie un nom de fichier des caractères illicites."""
    # Remplace les caractères invalides par un underscore
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)
    cleaned = cleaned.strip('. ')
    return cleaned or "sans_titre"
