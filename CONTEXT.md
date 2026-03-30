# CONTEXT.md — Point de reprise Tubor

> Dernière mise à jour : 2026-03-30
> Version courante : **v1.0.0**

---

## Architecture globale

```
tubor/
├── main.py                  # Point d'entrée — QApplication + MainWindow
├── requirements.txt         # PyQt6 >= 6.4, yt-dlp >= 2023.1.1
├── install.sh               # Script d'installation Linux (pip + .desktop)
├── INSTALL.md               # Guide d'installation alternatif
├── packaging/               # Packaging Debian (.deb)
│   ├── build-deb.sh         # Script de construction du paquet
│   └── debian/              # Structure DEBIAN/ + usr/
├── core/
│   ├── config.py            # Config persistante JSON → ~/.config/tubor/
│   ├── downloader.py        # DownloadWorker (QThread) + DownloadQueue
│   └── utils.py             # is_valid_url, send_desktop_notification, update_yt_dlp
└── ui/
    ├── main_window.py       # Fenêtre principale (splitter top/log)
    ├── settings_dialog.py   # Dialogue Paramètres + mise à jour yt-dlp
    ├── download_item.py     # Widget carte par téléchargement (progress bar)
    ├── help_dialog.py       # Aide intégrée (6 onglets)
    └── styles.py            # Thèmes QSS Catppuccin Mocha / Latte
```

---

## Fonctionnalités implémentées (v1.0.0)

### Phase 1 — Prototype
- [x] Interface PyQt6 de base
- [x] Lancement subprocess yt-dlp

### Phase 2 — MVP complet
- [x] File d'attente FIFO (DownloadQueue)
- [x] Progression en temps réel (%, vitesse, ETA) via regex sur stdout
- [x] Annulation fiable : SIGTERM → SIGKILL (pas d'API Python yt-dlp)
- [x] Détection immédiate de 18 patterns d'erreur fatale (403, privée, âge, etc.)
- [x] Post-traitement FFmpeg (fusion, métadonnées, miniature)
- [x] Dialogue Paramètres (dossier, format, qualité, cookies, thème)
- [x] Configuration persistante `~/.config/tubor/config.json`

### Phase 3 — Polish
- [x] Thèmes Catppuccin Mocha (sombre) + Latte (clair) — persistants
- [x] Notifications desktop via `notify-send`
- [x] Aide intégrée 6 onglets (Démarrage, Qualité, Playlist, Cookies, Thèmes, Raccourcis)
- [x] Mise à jour yt-dlp depuis l'interface (pip install -U dans thread)
- [x] Support playlists avec limite optionnelle
- [x] Support cookies (fichier Netscape)

### Phase 4 — Distribution (en cours)
- [x] Paquet Debian (.deb) — packaging/
- [x] Release GitHub v1.0.0 avec .deb en téléchargement
- [ ] AppImage (roadmap)
- [ ] Flatpak (roadmap)
- [ ] PyPI (roadmap)

---

## Détails techniques clés

### DownloadWorker (`core/downloader.py`)
- Utilise `subprocess.Popen` (pas l'API Python yt-dlp) pour annulation fiable
- Signaux PyQt : `progress_updated`, `log_message`, `finished_task`
- Parsing regex en temps réel :
  - `\[download\]\s+([\d.]+)%` → pourcentage
  - `at\s+([\d.]+\s*\w+/s)` → vitesse
  - `ETA\s+([\d:]+)` → temps restant
  - 18 patterns `_FATAL_PATTERNS` pour arrêt immédiat
- Post-processing détecté via `[Merger]`, `[EmbedThumbnail]`, `[Metadata]`

### Config (`core/config.py`)
- Chemin : `~/.config/tubor/config.json`
- Clés principales : `download_folder`, `format` (video/audio), `quality`, `theme` (dark/light), `embed_metadata`, `embed_thumbnail`, `use_cookies`, `cookie_file`, `playlist_mode`, `playlist_limit`

### UI Layout (`ui/main_window.py`)
- QMainWindow → QSplitter (panneau haut + log bas)
- Panneau haut : champ URL, toggle Video/Audio, qualité, boutons Download/Queue
- Cards de téléchargement : DownloadItemWidget (badge format + progress bar + bouton stop)
- Touche Échap = arrêt global

---

## Bugs connus

| # | Description | Statut |
|---|-------------|--------|
| 1 | `update_yt_dlp()` utilise `--break-system-packages` qui peut échouer sur certaines distros → fallback `--user` | Contourné dans install.sh, pas encore dans utils.py |
| 2 | La miniature embarquée (EmbedThumbnail) nécessite `mutagen` ou `AtomicParsley` — non détecté explicitement | Warning absent |
| 3 | Géométrie fenêtre non sauvegardée si l'app crashe | Cosmétique |
| 4 | Le scrollArea des download items ne défile pas automatiquement vers le bas | UX mineure |

---

## Ce sur quoi on travaillait en dernier

**Session 2026-03-30** : Publication de la release v1.0.0

1. Mise à jour du README avec icônes et markdown enrichi
2. Création du fichier CONTEXT.md (ce fichier)
3. Création du packaging Debian complet (`packaging/`)
4. Push sur https://github.com/nouhailler/tubor
5. Tag `v1.0.0` + Release GitHub avec .deb en pièce jointe

**Prochaine étape suggérée** : Phase 4 — créer un AppImage ou Flatpak pour une distribution plus large.

---

## Environnement de développement

```bash
# Lancer en dev
python3 main.py

# Construire le .deb
cd packaging && bash build-deb.sh

# Mettre à jour yt-dlp
pip install --upgrade yt-dlp
```

Dépendances système : `python3-pyqt6` ou pip PyQt6, `yt-dlp`, `ffmpeg` (optionnel), `dpkg-deb` (pour le build .deb).
