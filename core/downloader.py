"""
Tubor - Moteur de téléchargement via sous-processus yt-dlp
============================================================
On lance yt-dlp comme sous-processus (subprocess.Popen) plutôt que via l'API
Python. C'est la seule façon d'arrêter FIABLEMENT un téléchargement :
on appelle proc.terminate() → proc.kill() sans dépendre des threads internes
de yt-dlp ni de ses try/except.

Détection d'erreurs fatales (403, vidéo privée, etc.) en temps réel :
dès qu'une ligne d'erreur correspond, on tue le processus immédiatement.
"""

import re
import sys
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal


# ─────────────────────────────────────────────
#  Patterns de reconnaissance en temps réel
# ─────────────────────────────────────────────

# Progression : [download]  23.5% of  45.67MiB at  2.34MiB/s ETA 00:17
_RE_PROGRESS = re.compile(
    r'\[download\]\s+([\d.]+)%\s+of\s+~?([\d.,]+\s*\w+)\s+at\s+([\d.,~]+\s*\w+/s)\s+ETA\s+(\S+)',
    re.IGNORECASE,
)

# Destination (titre du fichier)
_RE_DESTINATION = re.compile(r'\[download\] Destination:\s+(.+)')
_RE_ALREADY_DL  = re.compile(r'\[download\] (.+) has already been downloaded')

# Erreurs fatales : (pattern_lowercase, message_français)
# La détection est immédiate — le processus est tué dès la première ligne correspondante.
FATAL_ERROR_PATTERNS: list[tuple[str, str]] = [
    ('http error 403',        'Accès refusé (HTTP 403 Forbidden). La vidéo est protégée ou votre IP est bloquée.'),
    ('403: forbidden',        'Accès refusé (HTTP 403 Forbidden). La vidéo est protégée ou votre IP est bloquée.'),
    ('private video',         'Cette vidéo est privée.'),
    ('video private',         'Cette vidéo est privée.'),
    ('video unavailable',     'Vidéo indisponible dans votre région ou supprimée.'),
    ('not available',         'Vidéo indisponible dans votre région.'),
    ('no space left',         'Espace disque insuffisant.'),
    ('login required',        'Connexion requise. Configurez vos cookies dans les Paramètres.'),
    ('sign in to confirm',    'Vidéo restreinte par âge. Configurez vos cookies dans les Paramètres.'),
    ('age-restricted',        'Vidéo restreinte par âge. Configurez vos cookies dans les Paramètres.'),
    ('copyright',             'Vidéo bloquée pour droits d\'auteur.'),
    ('http error 429',        'Trop de requêtes (HTTP 429). Veuillez réessayer plus tard.'),
    ('http error 401',        'Authentification requise (HTTP 401). Vérifiez vos cookies.'),
    ('unsupported url',       'URL non reconnue ou site non supporté par yt-dlp.'),
    ('unable to extract',     'Impossible d\'extraire les informations de la vidéo.'),
]


# ─────────────────────────────────────────────
#  Structures de données
# ─────────────────────────────────────────────

@dataclass
class DownloadTask:
    """Représente une tâche de téléchargement dans la file."""
    url: str
    format_type: str = "video"
    quality: str = "best"
    output_folder: str = ""
    playlist_mode: str = "single"
    playlist_limit: int = 0
    embed_metadata: bool = True
    embed_thumbnail: bool = True
    cookies_file: str = ""
    task_id: int = 0


@dataclass
class DownloadProgress:
    """État d'avancement d'un téléchargement."""
    task_id: int
    status: str = "waiting"         # waiting | downloading | processing | finished | error | cancelled
    filename: str = ""
    title: str = ""
    percent: float = 0.0
    speed: str = ""
    eta: str = ""
    downloaded_bytes: int = 0
    total_bytes: int = 0
    error_message: str = ""


# ─────────────────────────────────────────────
#  Utilitaires
# ─────────────────────────────────────────────

def is_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _ytdlp_executable() -> list[str]:
    """Retourne la commande pour lancer yt-dlp."""
    binary = shutil.which("yt-dlp")
    if binary:
        return [binary]
    return [sys.executable, "-m", "yt_dlp"]


def _check_fatal_error(line: str) -> str | None:
    """
    Détecte une erreur fatale dans une ligne de sortie yt-dlp.

    IMPORTANT : on cherche dans TOUTE la ligne, sans se limiter aux lignes
    préfixées par "ERROR:". En effet, les erreurs de fragments apparaissent
    sous la forme :
        [download] Got error: HTTP Error 403: Forbidden. Retrying fragment 1 (1/2)...
    qui ne contient pas "ERROR:" mais doit être détectée immédiatement.
    """
    # Filtre rapide : si "error" n'est nulle part, rien à faire
    if "error" not in line.lower():
        return None

    line_lower = line.lower()

    # ── Vérifie chaque pattern fatal (s'applique à toute la ligne) ──────
    for pattern, msg in FATAL_ERROR_PATTERNS:
        if pattern in line_lower:
            return msg

    # ── Pour les lignes explicitement préfixées par "ERROR:" (erreurs finales
    #    yt-dlp non reconnues dans nos patterns), on remonte le message brut ──
    if line.lstrip().startswith("ERROR:"):
        m = re.search(r'ERROR:\s*(.+)$', line)
        if m:
            return m.group(1).strip()[:250]

    # Ligne contient "error" mais n'est pas fatale (ex: warning retry 503, etc.)
    return None


# ─────────────────────────────────────────────
#  Thread de téléchargement (subprocess)
# ─────────────────────────────────────────────

class DownloadWorker(QThread):
    """
    QThread qui exécute yt-dlp en sous-processus.
    L'arrêt est fiable : on appelle proc.terminate() puis proc.kill().
    """

    progress_updated = pyqtSignal(object)   # DownloadProgress
    log_message      = pyqtSignal(str)
    finished_task    = pyqtSignal(object)   # DownloadProgress (final)

    def __init__(self, task: DownloadTask, parent=None):
        super().__init__(parent)
        self.task = task
        self._cancelled = False
        self._fatal_error: str | None = None
        self._proc: subprocess.Popen | None = None
        self._ffmpeg = is_ffmpeg_available()

    # ── Annulation ──────────────────────────────────────────────────────

    def cancel(self):
        """
        Arrêt NON-BLOQUANT (appelé depuis le thread UI).
        On envoie juste SIGTERM au processus et on retourne immédiatement.
        C'est run() qui attend la fin réelle du processus dans son propre thread.
        """
        self._cancelled = True
        proc = self._proc
        if proc and proc.poll() is None:
            try:
                proc.terminate()    # SIGTERM — non bloquant
            except OSError:
                pass

    def _kill_process_blocking(self):
        """
        Arrêt BLOQUANT — appelé uniquement depuis run() (dans le QThread).
        Attend la fin du processus et envoie SIGKILL si besoin.
        """
        proc = self._proc
        if proc is None or proc.poll() is not None:
            return
        try:
            proc.terminate()
            try:
                proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
        except OSError:
            pass

    # ── Boucle principale ───────────────────────────────────────────────

    def run(self):
        progress = DownloadProgress(task_id=self.task.task_id, status="downloading")
        self.progress_updated.emit(progress)

        try:
            cmd = self._build_command()
            self.log_message.emit(f"[CMD] {' '.join(cmd)}")

            # stderr=STDOUT : fusionne stderr dans stdout pour tout lire en un flux
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            title = ""

            # Lecture ligne par ligne
            for raw_line in self._proc.stdout:
                line = raw_line.rstrip()
                if not line:
                    continue

                # Filtre les lignes de débogage avant de les envoyer au journal
                if not line.startswith("[debug]"):
                    self.log_message.emit(line)

                # ── Erreur fatale immédiate ──────────────────────────
                fatal_msg = _check_fatal_error(line)
                if fatal_msg:
                    self._fatal_error = fatal_msg
                    self.log_message.emit(f"[ERREUR FATALE] {fatal_msg} — arrêt immédiat.")
                    self._kill_process_blocking()
                    break

                # ── Progression ──────────────────────────────────────
                m = _RE_PROGRESS.search(line)
                if m:
                    pct   = float(m.group(1))
                    speed = m.group(3).strip()
                    eta   = m.group(4).strip()
                    p = DownloadProgress(
                        task_id=self.task.task_id,
                        status="downloading",
                        percent=pct,
                        speed=speed,
                        eta=eta,
                        title=title,
                    )
                    self.progress_updated.emit(p)
                    continue

                # ── Destination / Titre ──────────────────────────────
                m2 = _RE_DESTINATION.match(line)
                if m2:
                    dest = m2.group(1).strip()
                    # Titre = nom de fichier sans l'extension
                    title = Path(dest).stem
                    progress.title = title
                    continue

                m3 = _RE_ALREADY_DL.match(line)
                if m3:
                    dest = m3.group(1).strip()
                    title = Path(dest).stem
                    continue

                # ── Post-traitement ffmpeg ───────────────────────────
                if any(tag in line for tag in (
                    "[ffmpeg]", "[ExtractAudio]", "[EmbedThumbnail]",
                    "[Merger]", "[MoveFiles]", "[Metadata]",
                )):
                    p = DownloadProgress(
                        task_id=self.task.task_id,
                        status="processing",
                        percent=99.0,
                        title=title,
                    )
                    self.progress_updated.emit(p)

            # ── Attente de fin du processus ──────────────────────────
            # Si cancel() a envoyé SIGTERM, on attend ici que le processus meure.
            if self._proc.poll() is None:
                try:
                    self._proc.wait(timeout=6)
                except subprocess.TimeoutExpired:
                    # Pas mort après 6s → SIGKILL
                    self._proc.kill()
                    self._proc.wait(timeout=3)

            returncode = self._proc.returncode

        except Exception as e:
            progress.status = "error"
            progress.error_message = f"Erreur inattendue : {e}"
            self.log_message.emit(f"[ERREUR INTERNE] {e}")
            self.finished_task.emit(progress)
            return

        # ── Résolution du statut final ────────────────────────────────
        if self._cancelled and self._fatal_error is None:
            progress.status = "cancelled"
            progress.error_message = "Arrêté par l'utilisateur"
            self.log_message.emit("[ARRÊT] Téléchargement stoppé.")

        elif self._fatal_error:
            progress.status = "error"
            progress.error_message = self._fatal_error
            self.log_message.emit(f"[ERREUR] {self._fatal_error}")

        elif returncode == 0:
            progress.status = "finished"
            progress.percent = 100.0
            progress.title = title
            self.log_message.emit(f"[OK] Terminé : {title or self.task.url}")

        else:
            progress.status = "error"
            progress.error_message = (
                f"yt-dlp a terminé avec le code {returncode}. "
                "Consultez le journal pour plus de détails."
            )

        self.finished_task.emit(progress)

    # ── Construction de la commande ─────────────────────────────────────

    def _build_command(self) -> list[str]:
        cmd = _ytdlp_executable()

        # ── Sortie ──────────────────────────────────────────────────────
        out_tpl = str(Path(self.task.output_folder) / "%(title)s.%(ext)s")
        cmd += ["-o", out_tpl]

        # ── Format ──────────────────────────────────────────────────────
        if self.task.format_type == "audio":
            cmd += ["-x", "--audio-format", "mp3"]
            q_map = {"mp3_320": "0", "mp3_192": "5", "mp3_128": "7", "best": "0"}
            cmd += ["--audio-quality", q_map.get(self.task.quality, "5")]
        else:
            fmt_map = {
                "best":  "bestvideo+bestaudio/best",
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
                "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
                "480p":  "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
                "360p":  "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
            }
            cmd += ["-f", fmt_map.get(self.task.quality, "bestvideo+bestaudio/best")]
            if self._ffmpeg:
                cmd += ["--merge-output-format", "mp4"]

        # ── Métadonnées / Miniature ──────────────────────────────────────
        if self._ffmpeg:
            if self.task.embed_metadata:
                cmd.append("--add-metadata")
            if self.task.embed_thumbnail:
                cmd.append("--embed-thumbnail")

        # ── Playlist ────────────────────────────────────────────────────
        if self.task.playlist_mode == "single":
            cmd.append("--no-playlist")
        elif self.task.playlist_limit > 0:
            cmd += ["--playlist-end", str(self.task.playlist_limit)]

        # ── Cookies ─────────────────────────────────────────────────────
        if self.task.cookies_file and Path(self.task.cookies_file).exists():
            cmd += ["--cookies", self.task.cookies_file]

        # ── Divers ──────────────────────────────────────────────────────
        cmd += [
            "--newline",          # Une ligne par mise à jour de progression
            "--no-warnings",      # Warnings dans les lignes ERROR uniquement
            "--retries", "2",
            "--fragment-retries", "2",
        ]

        cmd.append(self.task.url)
        return cmd


# ─────────────────────────────────────────────
#  File de téléchargement
# ─────────────────────────────────────────────

class DownloadQueue:
    def __init__(self):
        self._tasks: list[DownloadTask] = []
        self._counter = 0

    def add(self, task: DownloadTask) -> int:
        self._counter += 1
        task.task_id = self._counter
        self._tasks.append(task)
        return task.task_id

    def remove(self, task_id: int):
        self._tasks = [t for t in self._tasks if t.task_id != task_id]

    def clear(self):
        self._tasks.clear()

    def next(self) -> Optional[DownloadTask]:
        return self._tasks.pop(0) if self._tasks else None

    def peek(self) -> list[DownloadTask]:
        return list(self._tasks)

    def __len__(self):
        return len(self._tasks)
