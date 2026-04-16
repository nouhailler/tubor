# Changelog — Tubor

Toutes les modifications notables de ce projet sont documentées dans ce fichier.
Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [0.3.0] — 2026-04-16

### Quatre nouvelles fonctionnalités majeures

---

#### 1. 📊 Tableau de bord & Statistiques

- **`backend/core/database.py`** (nouveau) — Historique SQLite dans `~/.config/tubor/history.db`
  - Sauvegarde automatique de chaque téléchargement (terminé, erreur, annulé)
  - Détection automatique de la plateforme (YouTube, Twitch, Vimeo, TikTok, etc.)
  - Taille du fichier lue depuis le filesystem après téléchargement
- **`backend/api/routes/stats.py`** (nouveau) — 5 endpoints :
  - `GET /api/stats/summary` — total, réussis, échoués, aujourd'hui, taille totale, taux de succès
  - `GET /api/stats/daily?days=14` — histogramme quotidien
  - `GET /api/stats/platforms` — top plateformes
  - `GET /api/stats/formats` — répartition format/qualité avec durée moyenne
  - `GET /api/stats/history` — historique filtrable (statut, format) avec pagination
- **`frontend/src/components/Dashboard/Dashboard.tsx`** (nouveau) — Interface statistiques
  - 6 cartes récapitulatives avec code couleur
  - Graphique en barres CSS-only (14 derniers jours, jours manquants remplis)
  - Barres horizontales pour le top plateformes
  - Tableau d'historique avec filtres et badges de statut colorés
- Navigation principale dans `App.tsx` : onglets `⬇ Téléchargements` / `📊 Tableau de bord`

---

#### 2. 🔍 Prévisualisation avant téléchargement

- **`backend/api/routes/preview.py`** (nouveau)
  - Utilise `yt-dlp --dump-json` pour extraire les métadonnées sans télécharger
  - Extrait jusqu'à 12 formats uniques (résolution, codec, taille)
  - Détecte l'ID YouTube pour générer un lien d'embed `youtube-nocookie.com`
- **`frontend/src/components/PreviewModal/PreviewModal.tsx`** (nouveau)
  - Miniature cliquable → iframe YouTube 30s (domaine `youtube-nocookie.com`)
  - Grille métadonnées : auteur, durée, vues, date de mise en ligne
  - Table des formats disponibles repliable
  - Sélection format/qualité directement dans la modale + bouton Télécharger
  - Badge `🔴 LIVE` pour les streams en direct
- **`frontend/src/components/DownloadForm/DownloadForm.tsx`** — Bouton 🔍 dans la barre URL

---

#### 3. ⏱ Planification intelligente & Réorganisation de la file

- **Planification par téléchargement** : case ⏱ Planifier + sélecteur `datetime-local` dans le formulaire
  - Le bouton devient `⏱ PLANIFIER` ; le scheduler attend l'heure avant de démarrer
- **Mode Nuit tranquille** : dans les paramètres, fenêtre horaire configurable (défaut 2h–6h)
  - Les téléchargements en file se mettent automatiquement en pause hors fenêtre
- **Drag & drop de la file** : poignées `⋮⋮` sur les éléments en attente
  - HTML5 Drag-and-Drop API avec retour visuel (opacité + bordure accent)
  - Mise à jour optimiste côté React + synchronisation via `PUT /api/downloads/reorder`
- **Limite de bande passante** : champ `bandwidth_limit` (ex. `2M`, `500K`) → `--rate-limit`
- **`backend/core/downloader.py`** — `DownloadManager.reorder()`, `_is_night_blocking()`, `_tick()` avec vérification `scheduled_at`

---

#### 4. 🛡 Proxies & Robustesse anti-crash

- **Proxy unique** : champ `proxy` → `--proxy` (http://, https://, socks5://, socks4://)
- **Liste de proxies + rotation automatique** : round-robin entre les proxies configurés, un nouveau proxy est sélectionné à chaque téléchargement
- **Retry exponentiel** : backoff `10s → 20s → 40s → … max 5 min` sur erreurs transitoires (HTTP 429, 503, timeout, reset, fragment, 403)
- **Intervalle entre requêtes** : `sleep_interval` → `--sleep-interval` + `--max-sleep-interval`
- **Options de robustesse systématiques** : `--retries 5`, `--fragment-retries 5`, `--socket-timeout 30`, `--extractor-retries 3`
- **Statut `retrying`** : affiché dans la carte avec compte à rebours et couleur avertissement
- **Scheduler indestructible** : `_run_scheduler()` enveloppé dans `try/except` — le thread scheduler ne peut jamais mourir
- **`backend/core/config.py`** — Nouveaux champs : `proxy`, `proxy_list`, `proxy_rotation`, `max_retries`, `sleep_interval`, `bandwidth_limit`, `night_mode`, `night_start`, `night_end`
- **`frontend/src/components/SettingsModal/SettingsModal.tsx`** — Refonte en 5 onglets : Téléchargement, Réseau & Proxies, Planification, Auth, Moteur

---

## [0.2.0] — 2026-04-16

### Architecture — Migration vers une architecture web moderne

Cette release est une refonte complète de l'interface utilisateur.
La logique métier Python est conservée à l'identique ; seule la couche de présentation change.

#### Nouveau — Backend FastAPI (`backend/`)

- **`backend/main.py`** — Application FastAPI avec gestion du cycle de vie (lifespan), CORS pour le frontend Vite, et intégration WebSocket
- **`backend/core/config.py`** — Port du gestionnaire de configuration (sans dépendance Qt) ; même format JSON `~/.config/tubor/config.json`
- **`backend/core/downloader.py`** — Port du moteur de téléchargement :
  - `QThread` → `threading.Thread` avec callbacks Python
  - Signaux Qt → fonctions `on_progress`, `on_log`, `on_finish`
  - Nouveau `DownloadManager` singleton : gère la file, le scheduler et le broadcast asyncio
  - IDs de tâches passés d'entiers incrémentaux à UUID strings
- **`backend/core/utils.py`** — Utilitaires portés sans Qt (`is_valid_url`, `get_yt_dlp_version`, `update_yt_dlp`)
- **`backend/models/schemas.py`** — Schémas Pydantic pour la validation des entrées/sorties API
- **`backend/api/broadcast.py`** — `ConnectionManager` WebSocket thread-safe via `asyncio.run_coroutine_threadsafe`
- **`backend/api/websocket.py`** — Endpoint `WS /ws` : snapshot initial + broadcast temps réel des progressions
- **`backend/api/routes/downloads.py`** — Endpoints REST :
  - `GET  /api/downloads` — liste de tous les téléchargements
  - `POST /api/downloads` — ajouter à la file
  - `DELETE /api/downloads/{id}` — annuler un téléchargement
  - `DELETE /api/downloads` — annuler tous
  - `POST /api/downloads/clear-finished` — nettoyer les terminés
- **`backend/api/routes/config.py`** — `GET/PUT /api/config` — lire/modifier la configuration
- **`backend/api/routes/system.py`** — `GET /api/system` + `POST /api/system/update-ytdlp`
- **`backend/requirements.txt`** — `fastapi`, `uvicorn[standard]`, `websockets`, `yt-dlp`

#### Nouveau — Frontend React (`frontend/`)

- **Stack** : React 18 + TypeScript + Vite 5
- **`src/hooks/useWebSocket.ts`** — Hook de connexion WebSocket avec reconnexion automatique (2 s) et keepalive ping (20 s)
- **`src/hooks/useDownloads.ts`** — Hook principal : état des téléchargements synchronisé via WebSocket, tri par priorité de statut
- **`src/api/`** — Client HTTP léger (`fetch`) + endpoints typés pour downloads, config, system
- **`src/types/index.ts`** — Types TypeScript partagés (`DownloadItem`, `Config`, `WsEvent`, etc.)
- **Composants** :
  - `Header` — Barre de titre, bouton thème clair/sombre, bouton paramètres
  - `DownloadForm` — Formulaire complet : URL, format (vidéo/audio), qualité, mode playlist, dossier de destination
  - `DownloadCard` — Carte de téléchargement avec barre de progression temps réel, badges format, statut et annulation
  - `DownloadList` — Liste des téléchargements, barre d'état globale, bouton "tout arrêter", bouton "effacer les terminés"
  - `SettingsModal` — Modale paramètres à 3 onglets (Téléchargement, Authentification, Moteur yt-dlp)
  - `LogPanel` — Journal pliable/dépliable avec coloration syntaxique
- **Thème** : Catppuccin Mocha (dark) et Catppuccin Latte (light) via CSS custom properties, persisté en configuration

#### Infrastructure

- **`start.sh`** — Script de démarrage unifié : crée le venv Python, installe les dépendances npm, lance backend + frontend en parallèle avec arrêt propre (Ctrl+C)
- **`.gitignore`** mis à jour : `frontend/node_modules/`, `frontend/dist/`, `backend/.venv/`

#### Conservation de la logique métier

La logique suivante est **inchangée** par rapport à v0.1 :
- Construction de la commande `yt-dlp` (formats, qualités, options playlist, cookies)
- Détection temps réel des erreurs fatales (HTTP 403/401/429, vidéo privée, copyright, etc.)
- Post-traitement ffmpeg (fusion streams, métadonnées, miniatures)
- Annulation fiable via `SIGTERM` → `SIGKILL`
- Format de configuration JSON (`~/.config/tubor/config.json`)

---

## [0.1.0] — 2024

### Release initiale — Application desktop PyQt6

- Interface graphique desktop Linux via PyQt6
- Téléchargement vidéo/audio via yt-dlp (subprocess)
- File de téléchargements séquentielle
- Progression temps réel par carte individuelle
- Thèmes Catppuccin Mocha/Latte
- Support playlists avec limite optionnelle
- Post-traitement ffmpeg (métadonnées, miniatures, fusion MP4)
- Détection immédiate des erreurs fatales yt-dlp
- Mise à jour intégrée de yt-dlp
- Support cookies pour contenus restreints
- Notifications desktop (`notify-send`)
- Persistance configuration JSON
