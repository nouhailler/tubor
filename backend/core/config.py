"""
Tubor Web — Gestionnaire de configuration persistante
~/.config/tubor/config.json
"""

import json
from pathlib import Path

CONFIG_DIR  = Path.home() / ".config" / "tubor"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULTS: dict = {
    # Téléchargement
    "download_folder":   str(Path.home() / "Downloads"),
    "format":            "video",
    "quality":           "best",
    "theme":             "dark",
    "embed_metadata":    True,
    "embed_thumbnail":   True,
    "playlist_mode":     "single",
    "playlist_limit":    0,
    "cookies_file":      "",
    "concurrent_downloads": 1,

    # Réseau — Proxies
    "proxy_enabled":     True,      # Interrupteur rapide (On/Off sans perdre la config)
    "proxy":             "",        # URL unique  : "http://host:port" ou "socks5://host:port"
    "proxy_list":        [],        # Liste de proxies (rotation)
    "proxy_rotation":    False,     # Activer la rotation automatique

    # Réseau — Stabilité
    "max_retries":       3,         # Nombre maximum de tentatives automatiques
    "sleep_interval":    0,         # Secondes entre les requêtes (0 = désactivé)
    "bandwidth_limit":   "",        # Ex: "2M" = 2 MB/s, "" = illimité

    # Planification
    "night_mode":        False,     # Télécharger uniquement pendant la fenêtre nocturne
    "night_start":       2,         # Heure de début (0-23)
    "night_end":         6,         # Heure de fin   (0-23)

    # VPN rotation automatique
    "vpn_enabled":       False,     # Activer la rotation VPN
    "vpn_type":          "mullvad", # mullvad | nordvpn | protonvpn | expressvpn | custom
    "vpn_countries":     [],        # Liste de codes pays ISO : ["US","GB","DE","FR","NL"]
    "vpn_custom_cmd":    "",        # Commande personnalisée avec {country}/{COUNTRY}
    "vpn_reconnect_delay": 5,       # Secondes à attendre après changement de pays
}


class Config:

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._data: dict = {}
        self.load()

    def load(self):
        self._data = dict(DEFAULTS)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self._data.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
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

    def all(self) -> dict:
        return dict(self._data)

    def __getitem__(self, key):
        return self._data.get(key, DEFAULTS.get(key))

    def __setitem__(self, key, value):
        self._data[key] = value
