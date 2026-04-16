"""
Tubor Web — Historique des téléchargements (SQLite)
~/.config/tubor/history.db
"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path


DB_PATH = Path.home() / ".config" / "tubor" / "history.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS download_history (
    id             TEXT    PRIMARY KEY,
    url            TEXT    NOT NULL DEFAULT '',
    title          TEXT    NOT NULL DEFAULT '',
    format         TEXT    NOT NULL DEFAULT 'video',
    quality        TEXT    NOT NULL DEFAULT 'best',
    platform       TEXT    NOT NULL DEFAULT '',
    status         TEXT    NOT NULL DEFAULT '',
    file_size      INTEGER NOT NULL DEFAULT 0,
    filepath       TEXT    NOT NULL DEFAULT '',
    error_message  TEXT    NOT NULL DEFAULT '',
    started_at     REAL    NOT NULL DEFAULT 0,
    finished_at    REAL    NOT NULL DEFAULT 0,
    country_code   TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_started_at  ON download_history(started_at);
CREATE INDEX IF NOT EXISTS idx_status      ON download_history(status);
CREATE INDEX IF NOT EXISTS idx_platform    ON download_history(platform);
"""


def _detect_platform(url: str) -> str:
    u = url.lower()
    for domain, name in [
        ("youtube.com",    "YouTube"),
        ("youtu.be",       "YouTube"),
        ("vimeo.com",      "Vimeo"),
        ("twitch.tv",      "Twitch"),
        ("dailymotion.com","Dailymotion"),
        ("soundcloud.com", "SoundCloud"),
        ("twitter.com",    "Twitter/X"),
        ("x.com",          "Twitter/X"),
        ("instagram.com",  "Instagram"),
        ("tiktok.com",     "TikTok"),
        ("reddit.com",     "Reddit"),
        ("facebook.com",   "Facebook"),
        ("bilibili.com",   "Bilibili"),
        ("nicovideo.jp",   "NicoVideo"),
    ]:
        if domain in u:
            return name
    return "Autre"


class DownloadHistory:

    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(_SCHEMA)
            # Migration : ajouter country_code si absent (bases existantes)
            try:
                c.execute("ALTER TABLE download_history ADD COLUMN country_code TEXT NOT NULL DEFAULT ''")
            except sqlite3.OperationalError:
                pass  # Colonne déjà présente

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    # ── Écriture ─────────────────────────────────────────────────────────────

    def save(self, progress_dict: dict, started_at: float = 0):
        """Insère ou met à jour un enregistrement (upsert)."""
        filepath = progress_dict.get("filepath", "")
        file_size = 0
        if filepath and Path(filepath).exists():
            try:
                file_size = Path(filepath).stat().st_size
            except OSError:
                pass

        with self._conn() as c:
            c.execute("""
                INSERT OR REPLACE INTO download_history
                    (id, url, title, format, quality, platform, status,
                     file_size, filepath, error_message, started_at, finished_at,
                     country_code)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                progress_dict.get("id", ""),
                progress_dict.get("url", ""),
                progress_dict.get("title", ""),
                progress_dict.get("format", "video"),
                progress_dict.get("quality", "best"),
                _detect_platform(progress_dict.get("url", "")),
                progress_dict.get("status", ""),
                file_size,
                filepath,
                progress_dict.get("error_message", ""),
                started_at or time.time(),
                time.time(),
                progress_dict.get("country_code", ""),
            ))

    # ── Lecture ───────────────────────────────────────────────────────────────

    def get_history(self, limit: int = 100, offset: int = 0,
                    status_filter: str = "", format_filter: str = "") -> list[dict]:
        query = "SELECT * FROM download_history WHERE 1=1"
        params: list = []
        if status_filter:
            query += " AND status = ?"
            params.append(status_filter)
        if format_filter:
            query += " AND format = ?"
            params.append(format_filter)
        query += " ORDER BY finished_at DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        with self._conn() as c:
            return [dict(r) for r in c.execute(query, params).fetchall()]

    def get_summary(self) -> dict:
        today_ts = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        with self._conn() as c:
            total   = c.execute("SELECT COUNT(*) FROM download_history").fetchone()[0]
            success = c.execute("SELECT COUNT(*) FROM download_history WHERE status='finished'").fetchone()[0]
            failed  = c.execute("SELECT COUNT(*) FROM download_history WHERE status='error'").fetchone()[0]
            today   = c.execute("SELECT COUNT(*) FROM download_history WHERE started_at>=?", (today_ts,)).fetchone()[0]
            size    = c.execute("SELECT COALESCE(SUM(file_size),0) FROM download_history WHERE status='finished'").fetchone()[0]
        return {
            "total_downloads":      total,
            "successful_downloads": success,
            "failed_downloads":     failed,
            "today_downloads":      today,
            "total_size_bytes":     size,
            "success_rate":         round(success / total * 100, 1) if total else 0.0,
        }

    def get_daily(self, days: int = 14) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("""
                SELECT
                    date(started_at, 'unixepoch', 'localtime')          AS day,
                    COUNT(*)                                             AS count,
                    COALESCE(SUM(file_size), 0)                          AS size_bytes,
                    SUM(CASE WHEN status = 'finished' THEN 1 ELSE 0 END) AS count_success,
                    SUM(CASE WHEN status = 'error'    THEN 1 ELSE 0 END) AS count_error
                FROM download_history
                WHERE started_at > strftime('%s','now','-' || ? || ' days')
                GROUP BY day ORDER BY day
            """, (days,)).fetchall()
        return [dict(r) for r in rows]

    def get_platforms(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("""
                SELECT platform, COUNT(*) AS count
                FROM download_history
                WHERE platform != ''
                GROUP BY platform ORDER BY count DESC LIMIT 10
            """).fetchall()
        return [dict(r) for r in rows]

    def get_formats(self) -> list[dict]:
        with self._conn() as c:
            rows = c.execute("""
                SELECT
                    format, quality, COUNT(*) AS count,
                    ROUND(AVG(CASE WHEN status='finished' AND finished_at > started_at
                              THEN finished_at - started_at END), 1) AS avg_seconds
                FROM download_history
                GROUP BY format, quality ORDER BY count DESC
            """).fetchall()
        return [dict(r) for r in rows]


# Singleton
history = DownloadHistory()
