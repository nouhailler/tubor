# Tubor v0.3 — Contexte de développement

## Présentation du projet

Tubor est un téléchargeur vidéo (YouTube, et 1000+ sites) avec interface web.
- **Backend** : FastAPI (Python) — `backend/`
- **Frontend** : React + Vite + TypeScript — `frontend/src/`
- **Démarrage** : `./start.sh` (lance backend + frontend simultanément)
- **Config** : `~/.config/tubor/config.json`
- **DB** : SQLite `~/.config/tubor/tubor.db`

---

## Architecture

```
tubor/
├── start.sh
├── backend/
│   ├── main.py                  # FastAPI app, montage des routes
│   ├── requirements.txt         # fastapi, uvicorn, websockets, pydantic, yt-dlp
│   ├── core/
│   │   ├── config.py            # Lecture/écriture config JSON
│   │   ├── downloader.py        # DownloadManager, DownloadWorker, yt-dlp subprocess
│   │   ├── database.py          # SQLite (download_history)
│   │   └── utils.py             # is_valid_url, get_yt_dlp_version, update_yt_dlp
│   ├── api/
│   │   ├── broadcast.py         # WebSocket ConnectionManager
│   │   ├── routes/              # downloads, config, system, stats, preview
│   │   └── websocket.py         # /ws endpoint
│   └── models/
│       └── schemas.py           # Pydantic models (Responses, Requests)
└── frontend/src/
    ├── App.tsx                  # Navigation : 'main' | 'dashboard' | 'settings'
    ├── types/index.ts           # TypeScript interfaces
    ├── api/                     # client.ts, config.ts, downloads.ts, preview.ts, stats.ts, system.ts
    ├── hooks/
    │   ├── useDownloads.ts      # État downloads + WebSocket events
    │   └── useWebSocket.ts      # Connexion /ws
    └── components/
        ├── Header/              # Header.tsx + Header.css (thème toggle, bouton aide)
        ├── DownloadForm/        # DownloadForm.tsx + DownloadForm.css
        ├── DownloadList/        # DownloadList.tsx (drag & drop reorder)
        ├── DownloadCard/        # DownloadCard.tsx + DownloadCard.css
        ├── LogPanel/            # LogPanel.tsx (journal yt-dlp temps réel)
        ├── PreviewModal/        # PreviewModal.tsx (métadonnées avant téléchargement)
        ├── Dashboard/           # Dashboard.tsx + Dashboard.css
        ├── SettingsPage/        # SettingsPage.tsx + SettingsPage.css
        ├── SettingsModal/       # SettingsModal.css (styles modaux partagés)
        └── HelpModal/           # HelpModal.tsx + HelpModal.css (aide pleine page)
```

---

## Fonctionnalités implémentées

### Page Téléchargements (`DownloadForm` + `DownloadList`)
- Textarea multi-URL (une URL par ligne, badge compteur d'URLs)
- `extractUrls()` : parse et déduplique les URLs collées
- Bouton 📋 coller depuis le presse-papiers
- Bouton 🔍 prévisualisation (`PreviewModal`) : titre, durée, formats disponibles
- Sélection format (vidéo MP4 / audio MP3), qualité, dossier, playlist, planification
- **🌐 Proxy ON/OFF** : bascule `proxy_enabled` sans perdre la config proxy
- **🛡 VPN ON/OFF** : bascule `vpn_enabled` sans perdre la config VPN
- Drapeau pays affiché pendant le téléchargement (via `_resolve_country()`)
- **Drag & Drop** pour réordonner les items en attente dans la file
- Bouton 📂 Ouvrir le fichier après téléchargement
- `LogPanel` : journal yt-dlp en temps réel (rétractable, couleurs erreur/ok/cmd)

### Page Dashboard
- 4 onglets : Vue d'ensemble, Réussis, Échoués, Historique
- Cartes de stats cliquables (Réussis → onglet Réussis, Échoués → onglet Échoués)
- Onglet Réussis : titre, plateforme, format, taille, date
- Onglet Échoués : message d'erreur + bouton "📋 Copier URL" pour réessai + pays
- Graphe en barres empilées CSS (vert=succès, rouge=erreur) sur 14 jours
- Top plateformes (barres horizontales)
- Onglet Historique : filtres statut/format, tableau avec colonne Pays
- Auto-refresh toutes les 30s + bouton rafraîchissement manuel

### Page Paramètres (`SettingsPage`)
- Pleine page avec sidebar verticale (210px)
- 6 onglets : Téléchargement, Réseau & Proxies, VPN Auto, Planification, Authentification, Moteur
- **Téléchargement** : dossier, format/qualité préférés, métadonnées, miniature
- **Réseau & Proxies** : proxy unique, liste de proxies (rotation round-robin), tentatives max (backoff exponentiel), pause entre requêtes, limite bande passante
- **VPN Auto** : ProtonVPN, Mullvad, NordVPN, ExpressVPN, Custom. Pays en chips cliquables + textarea libre. Délai de reconnexion configurable.
  - Commande ProtonVPN : `/usr/bin/protonvpn disconnect && /usr/bin/protonvpn connect --country {COUNTRY}`
- **Planification** : Mode Nuit tranquille (fenêtre horaire configurable, supporte minuit)
- **Authentification** : fichier cookies Netscape
- **Moteur** : version yt-dlp, ffmpeg disponible, bouton mise à jour

### Aide (`HelpModal`)
- Pleine page avec scrollbar droite
- 7 onglets : Démarrage rapide, Formats & Qualités, Playlists & File, Réseau & Sécurité, Tableau de bord, Paramètres, Erreurs & Conseils

### Thème
- Sombre / clair (Catppuccin Mocha / Latte), persistant via config

---

## Backend — Points clés

### `config.py` — Valeurs par défaut
```python
DEFAULTS = {
    "proxy_enabled": True,
    "proxy_list": [],
    "proxy": "",
    "proxy_rotation": False,
    "max_retries": 3,
    "sleep_interval": 0,
    "bandwidth_limit": "",
    "vpn_enabled": False,
    "vpn_type": "protonvpn",
    "vpn_countries": [],
    "vpn_custom_cmd": "",
    "vpn_reconnect_delay": 5,
    "night_mode": False,
    "night_start": 22,
    "night_end": 6,
    "cookies_file": "",
    "theme": "dark",
    ...
}
```

### `downloader.py` — Fonctions importantes
```python
_normalize_proxy(proxy)          # http://IP:PORT:USER:PASS → http://USER:PASS@IP:PORT
_resolve_country(proxy)          # géolocalise l'IP (ip-api.com), cache own IP
_change_vpn_country(country)     # exécute la commande VPN CLI, invalide le cache IP
_is_bot_detection(output)        # détecte "sign in to confirm you're not a bot"
```

### Retry/rotation logique
- Bot-detection → retryable (dans `RETRYABLE_PATTERNS`)
- Sur retry : `task.proxy` vidé → `_tick()` appelle toujours `_next_proxy()`
- Si `proxy_enabled=False` → `_next_proxy()` retourne `""`
- Si bot-detection + VPN configuré → `_change_vpn_country()` avant retry

### `database.py` — Table `download_history`
Colonnes : `id, url, title, status, format, quality, folder, created_at, finished_at, country_code, platform, file_size, error_message`

### API Routes
- `GET/POST /api/downloads` — liste et ajout de téléchargements
- `DELETE /api/downloads/{id}` — annulation
- `POST /api/downloads/stop-all` — arrêt global
- `POST /api/downloads/clear-finished` — nettoyage
- `POST /api/downloads/reorder` — réordonnancement de la file
- `GET/PATCH /api/config` — configuration
- `GET /api/system` — version yt-dlp, ffmpeg
- `POST /api/system/update-ytdlp` — mise à jour yt-dlp
- `GET /api/stats/summary`, `/daily`, `/platforms`, `/history` — statistiques
- `GET /api/preview?url=` — métadonnées prévisualisation
- `WebSocket /ws` — événements temps réel (snapshot, added, progress, finished, reorder, log)

---

## Frontend — Points clés

### `types/index.ts`
```typescript
interface Config {
  proxy_enabled: boolean; vpn_enabled: boolean; vpn_type: string
  vpn_countries: string[]; vpn_custom_cmd: string; vpn_reconnect_delay: number
  proxy_rotation: boolean; max_retries: number; sleep_interval: number
  bandwidth_limit: string; night_mode: boolean; night_start: number; night_end: number
  cookies_file: string; theme: string; // ...
}
interface DownloadItem {
  id: string; url: string; title: string; status: string
  progress: number; speed: string; eta: string
  country_code: string; country_name: string; // ...
}
interface HistoryItem {
  id: string; url: string; title: string; status: string; platform: string
  country_code: string; file_size: number; error_message: string
  finished_at: number; format: string; quality: string; // ...
}
```

### WebSocket Events (`useWebSocket.ts`)
- `snapshot` : état complet à la connexion
- `added` : nouveau téléchargement ajouté
- `progress` / `finished` : mise à jour d'un téléchargement
- `reorder` : nouvel ordre de la file
- `log` : ligne de log yt-dlp

---

## Bugs corrigés (historique v0.3)

| Bug | Cause | Fix |
|-----|-------|-----|
| Écran blanc au démarrage | `proxyOn`, `toggleProxy`, etc. utilisés avant définition dans `DownloadForm.tsx` | Variables ajoutées avant le `return` |
| Type error `onAdd` | `Promise<DownloadItem>` vs `Promise<void>` dans les Props | Props changé en `Promise<unknown>` |
| Aide tronquée en bas | Modal avec `max-height: 88vh` | Converti en pleine page `position: fixed; inset: 0` |

---

## Commandes utiles

```bash
# Démarrer
./start.sh

# Vérifier import backend
cd backend && python -c "import main; print('OK')"

# Logs backend
# (affichés dans le terminal où start.sh tourne)

# Config actuelle
cat ~/.config/tubor/config.json

# DB
sqlite3 ~/.config/tubor/tubor.db ".schema"
sqlite3 ~/.config/tubor/tubor.db "SELECT * FROM download_history ORDER BY id DESC LIMIT 5;"

# Build frontend
cd frontend && npm run build
```

---

## État actuel (avril 2026)

- Version : **v0.3.0**
- Tout fonctionne : téléchargement, proxies, VPN ProtonVPN, dashboard, settings, help
- ProtonVPN testé et fonctionnel (NL→DE confirmé)
- Détection de pays via `ip-api.com` opérationnelle
- Toggles Proxy/VPN sur la page Téléchargements ✅
- Drag & drop reorder de la file ✅
- Prévisualisation avant téléchargement ✅
- LogPanel temps réel ✅
- Aide pleine page 7 onglets ✅
- Packaging Debian (.deb) ✅
- Release GitHub v0.3.0 ✅
