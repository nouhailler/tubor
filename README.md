<div align="center">
  <img src="resources/tubor.svg" width="120" alt="Tubor"/>

  # Tubor

  **Téléchargeur vidéo web** — YouTube, Vimeo, Twitch et 1 000+ sites

  [![Version](https://img.shields.io/badge/version-0.3.0-cba6f7?style=flat-square&logo=github)](https://github.com/nouhailler/tubor/releases)
  [![Python](https://img.shields.io/badge/Python-3.10%2B-89b4fa?style=flat-square&logo=python&logoColor=white)](https://python.org)
  [![Node](https://img.shields.io/badge/Node.js-18%2B-a6e3a1?style=flat-square&logo=node.js&logoColor=white)](https://nodejs.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115-94e2d5?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
  [![React](https://img.shields.io/badge/React-18-89dceb?style=flat-square&logo=react&logoColor=white)](https://react.dev)
  [![Licence](https://img.shields.io/badge/Licence-GPL%20v3-f38ba8?style=flat-square)](LICENSE)
  [![Linux](https://img.shields.io/badge/Platform-Linux-45475a?style=flat-square&logo=linux&logoColor=white)](https://kernel.org)
</div>

---

## ✨ Fonctionnalités

<table>
<tr>
<td width="50%">

**⬇ Téléchargement**
- Multi-URL — collez plusieurs URLs d'un coup
- Vidéo MP4 (360p → 1080p) ou Audio MP3 (128 → 320 kbps)
- Prévisualisation avant téléchargement 🔍
- Progression en temps réel (vitesse, ETA, %)
- Drag & drop pour réordonner la file
- Planification à une heure précise
- Ouverture directe du fichier après téléchargement

</td>
<td width="50%">

**🛡 Sécurité & Réseau**
- Toggle Proxy ON/OFF en un clic
- Rotation automatique de proxies (round-robin)
- VPN Auto — change de pays sur bot-detection YouTube
- Supporte ProtonVPN, Mullvad, NordVPN, ExpressVPN, Custom
- Drapeau pays affiché pendant le téléchargement
- Cookies Netscape pour contenus privés / membres

</td>
</tr>
<tr>
<td width="50%">

**📊 Tableau de bord**
- Statistiques globales en temps réel
- Graphique en barres empilées (14 jours)
- Top plateformes
- Historique filtrable (statut, format, pays)
- Copie URL des téléchargements échoués

</td>
<td width="50%">

**⚙ Configuration avancée**
- 6 onglets : Téléchargement, Réseau, VPN, Planification, Auth, Moteur
- Mode Nuit tranquille (fenêtre horaire configurable)
- Thème sombre / clair (Catppuccin Mocha / Latte)
- Mise à jour yt-dlp intégrée
- Journal temps réel (WebSocket)

</td>
</tr>
</table>

---

## 📸 Capture d'écran

<div align="center">

![Interface principale de Tubor](screenshots/tubor-main.png)

*Interface principale — thème Catppuccin Mocha (sombre)*

</div>

---

## 🚀 Installation rapide

### Option A — Paquet Debian (recommandé)

> Compatible **Ubuntu 22.04+**, **Debian 12+**, **Linux Mint 21+** et dérivés.

```bash
# Télécharger la dernière release
wget https://github.com/nouhailler/tubor/releases/latest/download/tubor_0.3.0_all.deb

# Installer
sudo dpkg -i tubor_0.3.0_all.deb
sudo apt-get install -f   # résoudre les dépendances si besoin

# Lancer
tubor
```

> L'entrée **Tubor** apparaît dans le menu des applications de votre bureau.

### Option B — Depuis les sources

```bash
git clone https://github.com/nouhailler/tubor.git
cd tubor
chmod +x start.sh
./start.sh
```

Puis ouvrez **http://localhost:5173** dans votre navigateur.

---

## 📋 Prérequis

| Outil | Version | Rôle |
|-------|---------|------|
| 🐍 Python | ≥ 3.10 | Backend FastAPI |
| 🟩 Node.js | ≥ 18 | Frontend React/Vite |
| 📦 npm | ≥ 9 | Gestion des dépendances JS |
| 🎬 ffmpeg | toute version récente | Conversion MP3, fusion flux HD *(optionnel)* |

```bash
# Ubuntu / Debian
sudo apt install python3 python3-venv nodejs npm ffmpeg
```

---

## 🏗 Architecture

```
tubor/
├── start.sh                 # Lance backend + frontend simultanément
├── backend/                 # API FastAPI (Python)
│   ├── main.py              # App FastAPI, montage des routes
│   ├── requirements.txt     # fastapi, uvicorn, websockets, pydantic, yt-dlp
│   ├── core/
│   │   ├── config.py        # Config JSON (~/.config/tubor/config.json)
│   │   ├── database.py      # SQLite historique (~/.config/tubor/tubor.db)
│   │   ├── downloader.py    # DownloadManager, rotation proxy/VPN, yt-dlp subprocess
│   │   └── utils.py         # Validation URL, version yt-dlp, mise à jour
│   ├── api/
│   │   ├── broadcast.py     # WebSocket ConnectionManager
│   │   ├── websocket.py     # Endpoint /ws (événements temps réel)
│   │   └── routes/          # downloads, config, system, stats, preview
│   └── models/
│       └── schemas.py       # Modèles Pydantic (Requests / Responses)
└── frontend/                # Interface React + TypeScript + Vite
    └── src/
        ├── App.tsx           # Navigation principale
        ├── api/              # Clients HTTP (config, downloads, stats, preview…)
        ├── hooks/            # useDownloads, useWebSocket
        └── components/       # Header, DownloadForm, DownloadList, Dashboard…
```

<details>
<summary><strong>🔌 API REST & WebSocket</strong></summary>

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/api/downloads` | Liste des téléchargements actifs |
| `POST` | `/api/downloads` | Ajouter un téléchargement |
| `DELETE` | `/api/downloads/{id}` | Annuler un téléchargement |
| `POST` | `/api/downloads/reorder` | Réordonner la file |
| `GET` | `/api/preview?url=` | Métadonnées avant téléchargement |
| `GET/PATCH` | `/api/config` | Lire / modifier la configuration |
| `GET` | `/api/stats/summary` | Statistiques globales |
| `GET` | `/api/stats/history` | Historique filtrable |
| `WS` | `/ws` | Événements temps réel |

</details>

---

## ⚡ Utilisation rapide

1. **Collez** une ou plusieurs URLs dans le champ (une par ligne)
2. Cliquez **🔍** pour prévisualiser la vidéo avant de télécharger *(optionnel)*
3. Choisissez **🎬 Vidéo** ou **🎵 Audio** et la qualité
4. Cliquez **⬇ TÉLÉCHARGER**
5. Suivez la progression dans la liste — cliquez **📂 Ouvrir** quand c'est fini

> **Anti-blocage** : activez les toggles **🌐 Proxy** et **🛡 VPN** sous le formulaire
> pour contourner les restrictions YouTube automatiquement.

---

## 🌙 Mode Nuit & Planification

```
Paramètres → Planification → Mode Nuit tranquille
```

Configurez une fenêtre horaire (ex : 22h → 6h) pour que Tubor dépose les téléchargements
en file et les exécute automatiquement la nuit. Fonctionne même sur les plages qui enjambent minuit.

---

## 🔒 Proxies & VPN

<details>
<summary><strong>Configurer un proxy</strong></summary>

Format accepté dans `Paramètres → Réseau & Proxies` :

```
http://host:port
http://host:port:user:pass      ← format court, normalisé automatiquement
socks5://host:port
```

Activez la **rotation automatique** pour changer de proxy à chaque téléchargement.
</details>

<details>
<summary><strong>Configurer le VPN Auto</strong></summary>

Dans `Paramètres → VPN Auto` :

1. Activez la rotation VPN
2. Choisissez votre client (ProtonVPN, Mullvad, NordVPN, ExpressVPN, Custom)
3. Sélectionnez les pays de rotation (chips cliquables ou codes ISO)

Sur détection de bot YouTube, Tubor exécute automatiquement la commande VPN,
attend la reconnexion, puis relance le téléchargement depuis la nouvelle IP.
</details>

---

## 📦 Construire le paquet Debian

```bash
chmod +x packaging/build_deb.sh
./packaging/build_deb.sh
# → génère dist/tubor_0.3.0_all.deb
```

---

## 🗺 Roadmap

- [x] Phase 1 — Prototype fonctionnel (PyQt6 desktop)
- [x] Phase 2 — Architecture web (FastAPI + React)
- [x] Phase 3 — Proxies, VPN Auto, Dashboard, Planification
- [x] Phase 4 — Packaging Debian, release GitHub
- [ ] Phase 5 — Mode serveur headless, API publique
- [ ] Authentification multi-utilisateurs
- [ ] Support Flatpak / AppImage

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

```bash
git checkout -b feature/ma-fonctionnalite
git commit -m 'feat: ajoute ma fonctionnalité'
git push origin feature/ma-fonctionnalite
# → ouvrir une Pull Request
```

---

## 📄 Licence

Ce projet est distribué sous licence **GPL v3**. Voir [LICENSE](LICENSE) pour les détails.

---

<div align="center">

Propulsé par [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [FastAPI](https://fastapi.tiangolo.com) · [React](https://react.dev) · [ffmpeg](https://ffmpeg.org)

</div>
