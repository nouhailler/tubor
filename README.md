<div align="center">

# 📥 Tubor

**Interface graphique Linux pour [yt-dlp](https://github.com/yt-dlp/yt-dlp)**
Simple par défaut · Puissant si besoin · 1000+ plateformes supportées

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4%2B-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![Licence](https://img.shields.io/badge/Licence-GPL%20v3-orange?style=for-the-badge&logo=gnu&logoColor=white)](LICENSE)
[![Linux](https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://kernel.org)
[![Release](https://img.shields.io/github/v/release/nouhailler/tubor?style=for-the-badge&logo=github&color=6e40c9)](https://github.com/nouhailler/tubor/releases)

</div>

---

## 📸 Aperçu

<div align="center">

![Interface principale de Tubor](screenshots/tubor-main.png)

*Interface principale — thème Catppuccin Mocha (sombre)*

</div>

---

## ✨ Fonctionnalités

<table>
<tr>
<td width="50%">

### 🎬 Téléchargement
- **Vidéo & Audio** — bascule d'un clic (MP4 / MP3)
- **Qualité** — 360p à 1080p · 128/192/320 kbps
- **File d'attente** — traitement séquentiel automatique
- **Playlists** — vidéo seule ou playlist entière (limite optionnelle)

### ⚡ Performance & Fiabilité
- **Progression temps réel** — vitesse, %, ETA par téléchargement
- **Arrêt instantané** — bouton Stop ×item ou touche `Échap`
- **Détection d'erreurs immédiate** — HTTP 403, vidéo privée, restriction d'âge…
- **Post-traitement FFmpeg** — fusion flux, métadonnées, miniature embarquée

</td>
<td width="50%">

### 🔒 Avancé
- **Support cookies** — vidéos restreintes par âge ou membres
- **Mise à jour yt-dlp** — bouton intégré dans les Paramètres
- **Notifications desktop** — alerte à la fin de chaque téléchargement

### 🎨 Expérience utilisateur
- **Thèmes Catppuccin** — Mocha (sombre) & Latte (clair)
- **Configuration persistante** — dossier, format, qualité sauvegardés
- **Aide intégrée** — 6 onglets (démarrage, qualité, playlist, cookies…)
- **HiDPI** — interface adaptée aux écrans haute résolution

</td>
</tr>
</table>

---

## 🚀 Installation rapide

### Option A — Paquet Debian `.deb` *(recommandé)*

> Fonctionne sur **Ubuntu 22.04+**, **Debian 12+**, **Linux Mint 21+** et dérivés.

```bash
# Télécharger la dernière release
wget https://github.com/nouhailler/tubor/releases/latest/download/tubor_1.0.0_all.deb

# Installer
sudo dpkg -i tubor_1.0.0_all.deb
sudo apt-get install -f   # résoudre les dépendances si nécessaire

# Lancer
tubor
```

### Option B — Script d'installation

```bash
git clone https://github.com/nouhailler/tubor.git
cd tubor
chmod +x install.sh && ./install.sh
python3 main.py
```

### Option C — Installation manuelle

```bash
git clone https://github.com/nouhailler/tubor.git
cd tubor
pip install --break-system-packages -r requirements.txt
python3 main.py
```

<details>
<summary><b>📦 Installer FFmpeg (recommandé pour la fusion vidéo/audio)</b></summary>

```bash
# Ubuntu / Debian
sudo apt install ffmpeg

# Fedora / RHEL
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg

# openSUSE
sudo zypper install ffmpeg
```

> FFmpeg est **optionnel** mais nécessaire pour fusionner les flux vidéo/audio, embarquer les métadonnées et les miniatures.

</details>

---

## 🎯 Utilisation rapide

```
1.  Collez une URL              →  YouTube, Vimeo, Twitch, Dailymotion…
2.  Choisissez 🎬 Vidéo ou 🎵 Audio
3.  Sélectionnez la qualité     →  360p / 720p / 1080p  ·  128 / 320 kbps
4.  Cliquez ⬇ TÉLÉCHARGER      →  ou + Ajouter à la file
5.  Suivez la progression       →  vitesse · % · ETA en temps réel
```

> 💡 **Raccourci :** `Échap` arrête tous les téléchargements en cours
> 💡 **Aide :** cliquez sur **❓** dans l'en-tête pour la documentation intégrée

---

## 🏗️ Architecture

```
tubor/
├── 📄 main.py                 # Point d'entrée — QApplication + MainWindow
├── 📋 requirements.txt        # Dépendances Python
├── 🔧 install.sh              # Script d'installation Linux
├── 📦 packaging/              # Packaging Debian (.deb)
│   ├── build-deb.sh
│   └── debian/
├── 🧠 core/
│   ├── config.py              # Config persistante → ~/.config/tubor/config.json
│   ├── downloader.py          # DownloadWorker (QThread) + subprocess yt-dlp
│   └── utils.py               # Validation URL · notifications · mise à jour
└── 🖥️ ui/
    ├── main_window.py         # Fenêtre principale
    ├── settings_dialog.py     # Dialogue Paramètres
    ├── download_item.py       # Widget carte par téléchargement
    ├── help_dialog.py         # Documentation intégrée (6 onglets)
    └── styles.py              # Thèmes QSS Catppuccin
```

---

## ⚙️ Détails techniques

<details>
<summary><b>🔧 Moteur de téléchargement</b></summary>

Tubor utilise `subprocess.Popen` pour lancer yt-dlp en processus séparé (pas l'API Python). Ce choix garantit :

| Avantage | Détail |
|----------|--------|
| **Annulation fiable** | `SIGTERM` → `SIGKILL` sans dépendre des hooks internes |
| **UI non bloquée** | Le téléchargement tourne dans un `QThread` |
| **Erreurs immédiates** | Chaque ligne stdout analysée en temps réel par regex |

18 patterns d'erreur fatale détectés : HTTP 403, vidéo privée, restriction d'âge, compte requis, vidéo supprimée…

</details>

<details>
<summary><b>📊 Prérequis système</b></summary>

| Outil | Version min. | Rôle |
|-------|-------------|------|
| 🐍 Python | **3.10+** | Environnement d'exécution |
| 🖼️ PyQt6 | **6.4+** | Interface graphique |
| 📹 yt-dlp | toute version récente | Moteur de téléchargement |
| 🎬 FFmpeg | toute version | *(optionnel)* Fusion · Métadonnées · Miniatures |

</details>

<details>
<summary><b>💾 Configuration</b></summary>

La configuration est sauvegardée dans `~/.config/tubor/config.json` :

```json
{
  "download_folder": "~/Téléchargements",
  "format": "video",
  "quality": "best",
  "theme": "dark",
  "embed_metadata": true,
  "embed_thumbnail": true,
  "use_cookies": false
}
```

</details>

---

## 🗺️ Roadmap

| Statut | Phase | Description |
|--------|-------|-------------|
| ✅ | Phase 1 | Prototype fonctionnel |
| ✅ | Phase 2 | MVP complet (file, progression, annulation, erreurs, paramètres) |
| ✅ | Phase 3 | Polish (thèmes, notifications, aide intégrée) |
| ✅ | Phase 4 | Distribution Debian `.deb` + Release GitHub |
| 🔄 | Phase 5 | AppImage · Flatpak · PyPI |
| 💡 | Futur | Analyse des formats disponibles avant téléchargement |
| 💡 | Futur | Stockage sécurisé des mots de passe via `keyring` |

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

```bash
# 1. Forkez le dépôt sur GitHub
# 2. Clonez votre fork
git clone https://github.com/<votre-pseudo>/tubor.git

# 3. Créez une branche
git checkout -b feature/ma-fonctionnalite

# 4. Commitez vos changements
git commit -m "feat: ajoute ma fonctionnalité"

# 5. Poussez et ouvrez une Pull Request
git push origin feature/ma-fonctionnalite
```

---

## 📜 Licence

Ce projet est distribué sous licence **GPL v3**. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 💖 Remerciements

| Projet | Rôle |
|--------|------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Le moteur qui fait tout le travail — 1000+ sites supportés |
| [FFmpeg](https://ffmpeg.org/) | Conversion, fusion et post-traitement multimédia |
| [Catppuccin](https://catppuccin.com/) | La palette de couleurs utilisée pour les thèmes |
| [PyQt6](https://riverbankcomputing.com/software/pyqt/) | Framework GUI Python pour Linux |

---

<div align="center">

**Fait avec ❤️ pour la communauté Linux**

[⬆ Haut de page](#-tubor) · [🐛 Signaler un bug](https://github.com/nouhailler/tubor/issues) · [💡 Proposer une feature](https://github.com/nouhailler/tubor/issues)

</div>
