"""
Tubor Web — Moteur de téléchargement robuste
=============================================
Améliorations v0.3 :
  - Proxy configurable par tâche + rotation automatique de liste
  - Retry exponentiel sur erreurs transitoires (429, 403, timeout…)
  - Planification : heure précise (scheduled_at) + mode nuit
  - Limite de bande passante (--rate-limit)
  - Intervalle entre requêtes (--sleep-interval)
  - Gestion d'erreurs exhaustive : aucune exception ne peut crasher le backend
  - Sauvegarde dans l'historique SQLite à chaque fin de téléchargement
"""

import json
import re
import sys
import shutil
import subprocess
import threading
import time
import uuid
import asyncio
import traceback
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from core.config import Config
from core.database import history

# ── Config singleton (relue à chaque usage pour refléter les changements UI) ─

def _cfg() -> Config:
    c = Config()
    c.load()
    return c


def _normalize_proxy(proxy: str) -> str:
    """
    Normalise un proxy vers le format attendu par yt-dlp.

    Formats acceptés en entrée :
      - http://host:port                     → inchangé
      - http://host:port:user:pass           → http://user:pass@host:port
      - socks5://host:port:user:pass         → socks5://user:pass@host:port
      - http://user:pass@host:port           → inchangé (déjà au bon format)

    Le format court « host:port:user:pass » est popularisé par les fournisseurs
    de proxies résidentiels et ne comporte pas de '@' dans la partie autorité.
    """
    proxy = proxy.strip()
    if not proxy:
        return proxy

    # Déjà au bon format (contient '@' dans la partie après le schéma)
    if '@' in proxy:
        return proxy

    # Extraire le schéma
    if '://' not in proxy:
        return proxy   # format inconnu, on laisse passer yt-dlp le rejeter

    scheme, rest = proxy.split('://', 1)
    # rest est de la forme : host:port  OU  host:port:user:pass
    parts = rest.split(':')

    if len(parts) == 4:
        # host:port:user:pass → user:pass@host:port
        host, port, user, password = parts
        return f"{scheme}://{user}:{password}@{host}:{port}"

    # 2 parts (host:port) ou autre → inchangé
    return proxy


# Cache pour l'IP propre du serveur (évite un appel par téléchargement)
_own_country_cache: tuple[str, str] | None = None
_own_country_lock = threading.Lock()


def _resolve_country(proxy: str) -> tuple[str, str]:
    """
    Retourne (country_code, country_name) correspondant à l'IP utilisée pour télécharger.

    - Avec proxy  → géolocalise l'IP du proxy (ce que YouTube voit)
    - Sans proxy  → géolocalise l'IP publique du serveur

    Utilise ip-api.com (HTTP, gratuit, 45 req/min).
    """
    global _own_country_cache

    host = ""
    if proxy:
        # Extraire le hostname depuis une URL proxy
        # formats: http://user:pass@host:port  ou  http://host:port
        m = re.search(r'@([^:/@\s]+):\d+', proxy) or re.search(r'://([^:/@\s]+):\d+', proxy)
        if m:
            host = m.group(1)

    # Si pas de proxy → réutiliser le cache de l'IP propre
    if not host:
        with _own_country_lock:
            if _own_country_cache is not None:
                return _own_country_cache

    try:
        url = f"http://ip-api.com/json/{host}?fields=countryCode,country,status"
        req = urllib.request.Request(url, headers={"User-Agent": "tubor/0.3"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read())
        if data.get("status") == "success":
            result = (data.get("countryCode", ""), data.get("country", ""))
            if not host:
                with _own_country_lock:
                    _own_country_cache = result
            return result
    except Exception:
        pass

    return ("", "")


# ── VPN country rotation ──────────────────────────────────────────────────────

# Commandes par type de VPN — {country} sera remplacé par le code ISO (ex: "us", "gb")
_VPN_COMMANDS: dict[str, str] = {
    "mullvad":    "mullvad relay set location {country} && mullvad reconnect",
    "nordvpn":    "nordvpn disconnect && nordvpn connect {country}",
    "protonvpn":  "/usr/bin/protonvpn disconnect && /usr/bin/protonvpn connect --country {COUNTRY}",
    "expressvpn": "expressvpn disconnect && expressvpn connect {country}",
}


def _change_vpn_country(country_code: str) -> bool:
    """
    Change le pays du VPN via son CLI.
    Retourne True si la commande a réussi.
    """
    cfg = _cfg()
    if not cfg.get("vpn_enabled", False):
        return False

    vpn_type   = cfg.get("vpn_type", "mullvad")
    custom_cmd = cfg.get("vpn_custom_cmd", "").strip()

    if vpn_type == "custom":
        cmd_tpl = custom_cmd
    else:
        cmd_tpl = _VPN_COMMANDS.get(vpn_type, "")

    if not cmd_tpl:
        return False

    # Remplacement des placeholders
    cmd = (cmd_tpl
           .replace("{country}",  country_code.lower())
           .replace("{COUNTRY}",  country_code.upper())
           .replace("{Country}",  country_code.capitalize()))

    try:
        result = subprocess.run(
            cmd, shell=True, timeout=45,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True,
        )
        reconnect_delay = int(cfg.get("vpn_reconnect_delay", 5))
        time.sleep(reconnect_delay)
        # Invalider le cache IP après changement de pays
        global _own_country_cache
        with _own_country_lock:
            _own_country_cache = None
        return result.returncode == 0
    except Exception:
        return False


# ── Patterns yt-dlp ──────────────────────────────────────────────────────────

_RE_PROGRESS = re.compile(
    r'\[download\]\s+([\d.]+)%\s+of\s+~?([\d.,]+\s*\w+)\s+at\s+([\d.,~]+\s*\w+/s)\s+ETA\s+(\S+)',
    re.IGNORECASE,
)
_RE_DESTINATION   = re.compile(r'\[download\] Destination:\s+(.+)')
_RE_ALREADY_DL    = re.compile(r'\[download\] (.+) has already been downloaded')
_RE_MERGER        = re.compile(r'\[Merger\] Merging formats into "(.+)"')
_RE_EXTRACT_AUDIO = re.compile(r'\[ExtractAudio\] Destination:\s+(.+)')
_RE_MOVE_FILES    = re.compile(r'\[MoveFiles\] Moving file (.+) to (.+)')

# Message conseil pour les erreurs de détection de bot
_BOT_DETECTION_HINT = (
    " · YouTube a détecté un bot depuis ce pays/IP. "
    "Essayez un proxy d'un autre pays ou configurez des cookies."
)

FATAL_ERROR_PATTERNS: list[tuple[str, str]] = [
    ("http error 403",     "Accès refusé (HTTP 403). La vidéo est protégée ou votre IP est bloquée."),
    ("403: forbidden",     "Accès refusé (HTTP 403). La vidéo est protégée ou votre IP est bloquée."),
    ("private video",      "Cette vidéo est privée."),
    ("video private",      "Cette vidéo est privée."),
    ("video unavailable",  "Vidéo indisponible dans votre région ou supprimée."),
    ("not available",      "Vidéo indisponible dans votre région."),
    ("no space left",      "Espace disque insuffisant."),
    ("login required",     "Connexion requise. Configurez vos cookies dans les Paramètres."),
    ("sign in to confirm", "YouTube bloque ce téléchargement (détection de bot)." + _BOT_DETECTION_HINT),
    ("age-restricted",     "Vidéo restreinte par âge. Configurez vos cookies."),
    ("copyright",          "Vidéo bloquée pour droits d'auteur."),
    ("unsupported url",    "URL non reconnue ou site non supporté par yt-dlp."),
    ("unable to extract",  "Impossible d'extraire les informations de la vidéo."),
]

RETRYABLE_PATTERNS: list[str] = [
    "http error 429",
    "http error 503",
    "trop de requêtes",
    "too many requests",
    "connection reset",
    "connection timed out",
    "timed out",
    "network error",
    "fragment",
    "unable to download",
    "http error 403",
    "accès refusé",
    # Détection de bot → retryable si proxy/VPN configuré
    "détection de bot",
    "sign in to confirm",
    "not a bot",
]

# Patterns indiquant spécifiquement une détection de bot (changement IP/VPN utile)
BOT_DETECTION_PATTERNS: list[str] = [
    "détection de bot",
    "sign in to confirm",
    "not a bot",
]


def _is_bot_detection(error: str) -> bool:
    el = error.lower()
    return any(p in el for p in BOT_DETECTION_PATTERNS)


# ── Structures de données ─────────────────────────────────────────────────────

@dataclass
class DownloadTask:
    url: str
    format_type: str    = "video"
    quality: str        = "best"
    output_folder: str  = ""
    playlist_mode: str  = "single"
    playlist_limit: int = 0
    embed_metadata: bool  = True
    embed_thumbnail: bool = True
    cookies_file: str   = ""
    task_id: str        = field(default_factory=lambda: str(uuid.uuid4()))
    # Nouveaux champs
    scheduled_at: float = 0.0   # Unix timestamp, 0 = immédiat
    proxy: str          = ""    # Proxy spécifique à cette tâche
    bandwidth_limit: str = ""   # ex: "2M"
    sleep_interval: int = 0     # secondes entre les requêtes
    country_code: str   = ""    # Code ISO 2 lettres résolu au démarrage


@dataclass
class DownloadProgress:
    task_id: str
    url: str         = ""
    format_type: str = ""
    quality: str     = ""
    status: str      = "waiting"
    filename: str    = ""
    filepath: str    = ""
    title: str       = ""
    percent: float   = 0.0
    speed: str       = ""
    eta: str         = ""
    error_message: str = ""
    retry_count: int  = 0   # Nombre de tentatives effectuées
    country_code: str = ""  # ISO 2 lettres de l'IP/proxy utilisé
    country_name: str = ""  # Nom complet du pays

    def to_dict(self) -> dict:
        return {
            "id":            self.task_id,
            "url":           self.url,
            "format":        self.format_type,
            "quality":       self.quality,
            "status":        self.status,
            "title":         self.title,
            "filename":      self.filename,
            "filepath":      self.filepath,
            "percent":       self.percent,
            "speed":         self.speed,
            "eta":           self.eta,
            "error_message": self.error_message,
            "retry_count":   self.retry_count,
            "country_code":  self.country_code,
            "country_name":  self.country_name,
        }


# ── Utilitaires ───────────────────────────────────────────────────────────────

def is_ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _ytdlp_executable() -> list[str]:
    binary = shutil.which("yt-dlp")
    return [binary] if binary else [sys.executable, "-m", "yt_dlp"]


def _check_fatal_error(line: str) -> str | None:
    if "error" not in line.lower():
        return None
    ll = line.lower()
    for pattern, msg in FATAL_ERROR_PATTERNS:
        if pattern in ll:
            return msg
    if line.lstrip().startswith("ERROR:"):
        m = re.search(r"ERROR:\s*(.+)$", line)
        if m:
            return m.group(1).strip()[:250]
    return None


def _is_retryable(error: str) -> bool:
    el = error.lower()
    return any(p in el for p in RETRYABLE_PATTERNS)


def _fmt_seconds(s: float) -> str:
    s = int(s)
    h, rem = divmod(s, 3600)
    m, sc  = divmod(rem, 60)
    return f"{h}:{m:02d}:{sc:02d}" if h else f"{m}:{sc:02d}"


# ── Worker ────────────────────────────────────────────────────────────────────

class DownloadWorker(threading.Thread):

    def __init__(
        self,
        task: DownloadTask,
        on_progress: Callable[[DownloadProgress], None],
        on_log:      Callable[[str, str], None],
        on_finish:   Callable[[DownloadProgress], None],
    ):
        super().__init__(daemon=True)
        self.task         = task
        self._on_progress = on_progress
        self._on_log      = on_log
        self._on_finish   = on_finish
        self._cancelled   = False
        self._fatal_error: str | None = None
        self._proc: subprocess.Popen | None = None
        self._ffmpeg      = is_ffmpeg_available()

    def cancel(self):
        self._cancelled = True
        proc = self._proc
        if proc and proc.poll() is None:
            try:
                proc.terminate()
            except OSError:
                pass

    def _kill_blocking(self):
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

    def run(self):
        progress = DownloadProgress(
            task_id=self.task.task_id, url=self.task.url,
            format_type=self.task.format_type, quality=self.task.quality,
            status="downloading",
        )

        # Résoudre le pays de l'IP/proxy utilisé (non bloquant : ~200ms)
        try:
            code, name = _resolve_country(self.task.proxy)
            progress.country_code = code
            progress.country_name = name
        except Exception:
            pass

        self._on_progress(progress)

        try:
            cmd = self._build_command()
            self._on_log(self.task.task_id, f"[CMD] {' '.join(cmd)}")

            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
            )

            title    = ""
            filepath = ""

            for raw_line in self._proc.stdout:
                line = raw_line.rstrip()
                if not line:
                    continue
                if not line.startswith("[debug]"):
                    self._on_log(self.task.task_id, line)

                # Erreur fatale immédiate
                fatal = _check_fatal_error(line)
                if fatal:
                    self._fatal_error = fatal
                    self._on_log(self.task.task_id, f"[ERREUR FATALE] {fatal}")
                    self._kill_blocking()
                    break

                # Progression
                m = _RE_PROGRESS.search(line)
                if m:
                    progress = DownloadProgress(
                        task_id=self.task.task_id, url=self.task.url,
                        format_type=self.task.format_type, quality=self.task.quality,
                        status="downloading",
                        percent=float(m.group(1)),
                        speed=m.group(3).strip(),
                        eta=m.group(4).strip(),
                        title=title, filepath=filepath,
                    )
                    self._on_progress(progress)
                    continue

                # Destination initiale
                m2 = _RE_DESTINATION.match(line)
                if m2:
                    dest = m2.group(1).strip()
                    title = Path(dest).stem; filepath = dest
                    progress.title = title; progress.filepath = filepath
                    continue

                m3 = _RE_ALREADY_DL.match(line)
                if m3:
                    dest = m3.group(1).strip()
                    title = Path(dest).stem; filepath = dest
                    continue

                # Fichier final (après fusion / conversion)
                for rx, grp in [(_RE_MERGER, 1), (_RE_EXTRACT_AUDIO, 1)]:
                    mm = rx.search(line)
                    if mm:
                        filepath = mm.group(grp).strip()
                        title    = Path(filepath).stem

                mm = _RE_MOVE_FILES.search(line)
                if mm:
                    filepath = mm.group(2).strip()
                    title    = Path(filepath).stem

                # Post-traitement ffmpeg
                if any(t in line for t in (
                    "[ffmpeg]","[ExtractAudio]","[EmbedThumbnail]",
                    "[Merger]","[MoveFiles]","[Metadata]",
                )):
                    progress = DownloadProgress(
                        task_id=self.task.task_id, url=self.task.url,
                        format_type=self.task.format_type, quality=self.task.quality,
                        status="processing", percent=99.0,
                        title=title, filepath=filepath,
                    )
                    self._on_progress(progress)

            # Attente propre
            if self._proc.poll() is None:
                try:
                    self._proc.wait(timeout=6)
                except subprocess.TimeoutExpired:
                    self._proc.kill()
                    self._proc.wait(timeout=3)

            returncode = self._proc.returncode

        except Exception as exc:
            tb = traceback.format_exc()
            self._on_log(self.task.task_id, f"[ERREUR INTERNE] {exc}\n{tb}")
            progress.status        = "error"
            progress.error_message = f"Erreur interne : {exc}"
            self._on_finish(progress)
            return

        # Résolution finale
        if self._cancelled and not self._fatal_error:
            progress.status        = "cancelled"
            progress.error_message = "Arrêté par l'utilisateur"
        elif self._fatal_error:
            progress.status        = "error"
            progress.error_message = self._fatal_error
        elif returncode == 0:
            progress.status   = "finished"
            progress.percent  = 100.0
            progress.title    = title
            progress.filepath = filepath
        else:
            progress.status        = "error"
            progress.error_message = (
                f"yt-dlp a terminé avec le code {returncode}. "
                "Consultez le journal pour plus de détails."
            )

        self._on_finish(progress)

    def _build_command(self) -> list[str]:
        cfg = _cfg()
        cmd = _ytdlp_executable()

        # Sortie
        out_tpl = str(Path(self.task.output_folder) / "%(title)s.%(ext)s")
        cmd += ["-o", out_tpl]

        # Format
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

        # Métadonnées / miniature
        if self._ffmpeg:
            if self.task.embed_metadata:
                cmd.append("--add-metadata")
            if self.task.embed_thumbnail:
                cmd.append("--embed-thumbnail")

        # Playlist
        if self.task.playlist_mode == "single":
            cmd.append("--no-playlist")
        elif self.task.playlist_limit > 0:
            cmd += ["--playlist-end", str(self.task.playlist_limit)]

        # Cookies
        if self.task.cookies_file and Path(self.task.cookies_file).exists():
            cmd += ["--cookies", self.task.cookies_file]

        # ── Proxy ──────────────────────────────────────────────────────────
        proxy = _normalize_proxy(self.task.proxy or cfg.get("proxy", ""))
        if proxy:
            cmd += ["--proxy", proxy]

        # ── Limite de bande passante ──────────────────────────────────────
        bw = self.task.bandwidth_limit or cfg.get("bandwidth_limit", "")
        if bw:
            cmd += ["--rate-limit", bw]

        # ── Intervalle entre requêtes ─────────────────────────────────────
        sleep = self.task.sleep_interval or int(cfg.get("sleep_interval", 0))
        if sleep > 0:
            cmd += ["--sleep-interval", str(sleep),
                    "--max-sleep-interval", str(sleep * 3)]

        # ── Options de robustesse ─────────────────────────────────────────
        cmd += [
            "--newline",
            "--no-warnings",
            "--retries",           "5",
            "--fragment-retries",  "5",
            "--socket-timeout",    "30",
            "--extractor-retries", "3",
        ]

        cmd.append(self.task.url)
        return cmd


# ── DownloadManager ───────────────────────────────────────────────────────────

class DownloadManager:
    """
    Gère la file, le scheduler (avec planification + mode nuit),
    les retries exponentiels, la rotation de proxies
    et le broadcast WebSocket.
    """

    def __init__(self):
        self._progress: dict[str, DownloadProgress] = {}
        self._queue: list[str]                       = []
        self._lock                                   = threading.Lock()
        self._active_worker: Optional[DownloadWorker] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Retry
        self._retry_counts: dict[str, int] = {}
        self._start_times:  dict[str, float] = {}

        # Proxy / VPN rotation
        self._proxy_index       = 0
        self._vpn_country_index = 0

        self._scheduler = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler.start()

    # ── Cycle de vie ─────────────────────────────────────────────────────────

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    # ── API publique ──────────────────────────────────────────────────────────

    def add(self, task: DownloadTask) -> DownloadProgress:
        progress = DownloadProgress(
            task_id=task.task_id, url=task.url,
            format_type=task.format_type, quality=task.quality,
            status="waiting",
        )
        with self._lock:
            self._progress[task.task_id] = progress
            self._queue.append(task.task_id)
            self._start_times[task.task_id] = time.time()
        self._broadcast({"type": "added", "data": progress.to_dict(),
                         "queue_order": self._queue_snapshot()})
        return progress

    def cancel(self, task_id: str):
        with self._lock:
            if task_id in self._queue:
                self._queue.remove(task_id)
                if task_id in self._progress:
                    self._progress[task_id].status = "cancelled"
                    self._broadcast({"type": "progress", "data": self._progress[task_id].to_dict()})
                return
        worker = self._active_worker
        if worker and worker.task.task_id == task_id:
            worker.cancel()

    def cancel_all(self):
        with self._lock:
            for tid in list(self._queue):
                if tid in self._progress:
                    self._progress[tid].status = "cancelled"
                    self._broadcast({"type": "progress", "data": self._progress[tid].to_dict()})
            self._queue.clear()
        worker = self._active_worker
        if worker:
            worker.cancel()

    def clear_finished(self):
        with self._lock:
            done = [tid for tid, p in self._progress.items()
                    if p.status in ("finished", "error", "cancelled")]
            for tid in done:
                del self._progress[tid]
                self._retry_counts.pop(tid, None)
                self._start_times.pop(tid, None)

    def reorder(self, new_order: list[str]):
        with self._lock:
            waiting = [tid for tid in new_order if tid in self._queue]
            rest    = [tid for tid in self._queue if tid not in waiting]
            self._queue = waiting + rest
        self._broadcast({"type": "reorder", "queue_order": self._queue_snapshot()})

    def get_all(self) -> list[dict]:
        with self._lock:
            return [p.to_dict() for p in self._progress.values()]

    def get_queue_order(self) -> list[str]:
        with self._lock:
            return list(self._queue)

    # ── Scheduler ─────────────────────────────────────────────────────────────

    def _run_scheduler(self):
        while True:
            try:
                self._tick()
            except Exception:
                pass  # Ne jamais laisser le scheduler mourir
            time.sleep(0.5)

    def _tick(self):
        task_id: str | None = None
        with self._lock:
            if self._queue and self._active_worker is None:
                next_id = self._queue[0]
                task = _task_store.get(next_id)

                # 1. Vérifier l'heure planifiée
                if task and task.scheduled_at and time.time() < task.scheduled_at:
                    return   # Pas encore l'heure

                # 2. Vérifier le mode nuit
                if self._is_night_blocking():
                    return

                task_id = self._queue.pop(0)

        if not task_id:
            return

        task = _task_store.get(task_id)
        if not task:
            return

        # Toujours recalculer le proxy (rotation) — même sur retry
        task.proxy = self._next_proxy()

        worker = DownloadWorker(
            task=task,
            on_progress=self._on_progress,
            on_log=self._on_log,
            on_finish=self._on_finish,
        )
        with self._lock:
            self._active_worker = worker
        worker.start()
        worker.join()
        with self._lock:
            self._active_worker = None

    def _is_night_blocking(self) -> bool:
        """True si le mode nuit est actif et on est EN DEHORS de la fenêtre."""
        cfg = _cfg()
        if not cfg.get("night_mode", False):
            return False
        now   = datetime.now().hour
        start = int(cfg.get("night_start", 2))
        end   = int(cfg.get("night_end",   6))
        if start <= end:
            in_window = start <= now < end
        else:
            in_window = now >= start or now < end
        return not in_window

    def _next_proxy(self) -> str:
        cfg = _cfg()
        if not cfg.get("proxy_enabled", True):
            return ""   # Interrupteur OFF → pas de proxy
        proxies = cfg.get("proxy_list", [])
        if proxies and cfg.get("proxy_rotation", False):
            p = proxies[self._proxy_index % len(proxies)]
            self._proxy_index += 1
            return _normalize_proxy(p)
        return _normalize_proxy(cfg.get("proxy", ""))

    def _next_vpn_country(self) -> str:
        """Retourne le prochain pays VPN en rotation, ou '' si non configuré."""
        cfg = _cfg()
        if not cfg.get("vpn_enabled", False):
            return ""
        countries = [c.strip() for c in cfg.get("vpn_countries", []) if c.strip()]
        if not countries:
            return ""
        country = countries[self._vpn_country_index % len(countries)]
        self._vpn_country_index += 1
        return country

    # ── Callbacks workers ──────────────────────────────────────────────────────

    def _on_progress(self, p: DownloadProgress):
        with self._lock:
            prev = self._progress.get(p.task_id)
            if prev:
                p.retry_count = prev.retry_count
                if not p.country_code and prev.country_code:
                    p.country_code = prev.country_code
                    p.country_name = prev.country_name
            self._progress[p.task_id] = p
        self._broadcast({"type": "progress", "data": p.to_dict()})

    def _on_log(self, task_id: str, message: str):
        self._broadcast({"type": "log", "task_id": task_id, "message": message})

    def _on_finish(self, p: DownloadProgress):
        with self._lock:
            prev = self._progress.get(p.task_id)
            if prev:
                p.retry_count = prev.retry_count
                if not p.country_code and prev.country_code:
                    p.country_code = prev.country_code
                    p.country_name = prev.country_name
            self._progress[p.task_id] = p

        # Sauvegarder dans l'historique
        if p.status in ("finished", "error", "cancelled"):
            try:
                history.save(p.to_dict(), started_at=self._start_times.get(p.task_id, 0))
            except Exception as exc:
                print(f"[History] Erreur de sauvegarde : {exc}")

        # Retry exponentiel sur erreurs transitoires
        if p.status == "error" and _is_retryable(p.error_message):
            cfg = _cfg()
            max_retries = int(cfg.get("max_retries", 3))
            retries = self._retry_counts.get(p.task_id, 0)
            is_bot = _is_bot_detection(p.error_message)

            # Pour une détection de bot sans proxy/VPN disponible → pas de retry inutile
            has_rotation = (
                (cfg.get("proxy_rotation", False) and cfg.get("proxy_list", [])) or
                (cfg.get("vpn_enabled", False) and cfg.get("vpn_countries", []))
            )
            if is_bot and not has_rotation:
                # Pas de moyen de changer d'IP → on ne retry pas
                pass
            elif retries < max_retries:
                self._retry_counts[p.task_id] = retries + 1
                delay = min(2 ** (retries + 1) * 5, 300)  # 10s, 20s, 40s…max 5min

                # Si détection de bot + VPN → changer de pays avant le délai
                vpn_country = ""
                if is_bot:
                    vpn_country = self._next_vpn_country()
                    if vpn_country:
                        delay = max(delay, 8)  # laisser au moins 8s au VPN

                self._on_log(
                    p.task_id,
                    f"[RETRY] {'Détection bot' if is_bot else 'Erreur transitoire'}"
                    f" — tentative {retries + 1}/{max_retries} dans {delay}s"
                    + (f" via VPN {vpn_country}" if vpn_country else "")
                )
                p.status        = "retrying"
                p.error_message = (
                    f"Tentative {retries + 1}/{max_retries} dans {delay}s"
                    + (f" (VPN → {vpn_country})" if vpn_country else "")
                )
                p.retry_count   = retries + 1
                self._broadcast({"type": "progress", "data": p.to_dict()})

                def _delayed_retry(tid=p.task_id, d=delay, vc=vpn_country):
                    # Changer le pays VPN en arrière-plan pendant le délai
                    if vc:
                        threading.Thread(
                            target=_change_vpn_country,
                            args=(vc,),
                            daemon=True,
                        ).start()
                    time.sleep(d)
                    task = _task_store.get(tid)
                    if task:
                        task.proxy = ""  # forcer réassignation du proxy dans _tick
                    with self._lock:
                        if tid in self._progress:
                            self._progress[tid].status        = "waiting"
                            self._progress[tid].error_message = ""
                            self._progress[tid].percent       = 0.0
                            self._queue.append(tid)
                    self._broadcast({"type": "progress",
                                     "data": self._progress[tid].to_dict()})
                threading.Thread(target=_delayed_retry, daemon=True).start()
                return

        self._broadcast({"type": "finished", "data": p.to_dict()})

    # ── Broadcast ──────────────────────────────────────────────────────────────

    def _broadcast(self, event: dict):
        if self._loop is None or self._loop.is_closed():
            return
        try:
            from api.broadcast import manager as bm
            asyncio.run_coroutine_threadsafe(bm.broadcast(event), self._loop)
        except Exception:
            pass

    def _queue_snapshot(self) -> list[str]:
        return list(self._queue)


# ── Stockage global des tâches complètes ─────────────────────────────────────

_task_store: dict[str, DownloadTask] = {}

# Singleton
download_manager = DownloadManager()
