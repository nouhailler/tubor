# 📦 Guide d'installation — Tubor

## Méthode 1 — Paquet Debian (recommandée)

> Compatible : Ubuntu 22.04+, Debian 12+, Linux Mint 21+, et dérivés

```bash
# Télécharger le paquet
wget https://github.com/nouhailler/tubor/releases/latest/download/tubor_1.0.0_all.deb

# Installer avec gestion automatique des dépendances
sudo apt install ./tubor_1.0.0_all.deb

# Lancer
tubor
```

Tubor apparaît ensuite dans le menu des applications sous **Internet** ou **Multimédia**.

---

## Méthode 2 — Script d'installation automatique

```bash
git clone https://github.com/nouhailler/tubor.git
cd tubor
chmod +x install.sh
./install.sh
```

Le script :
1. Vérifie Python 3.10+
2. Détecte FFmpeg (et prévient si absent)
3. Installe les dépendances Python
4. Crée un raccourci `.desktop` dans le menu des applications

---

## Méthode 3 — Installation manuelle

### Étape 1 — Cloner le dépôt

```bash
git clone https://github.com/nouhailler/tubor.git
cd tubor
```

### Étape 2 — Installer les dépendances Python

```bash
# Méthode pip avec isolation système
pip install --break-system-packages -r requirements.txt

# Ou dans un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Étape 3 — Installer FFmpeg (optionnel mais recommandé)

| Distribution | Commande |
|-------------|----------|
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora | `sudo dnf install ffmpeg` |
| Arch Linux | `sudo pacman -S ffmpeg` |
| openSUSE | `sudo zypper install ffmpeg` |

> FFmpeg est nécessaire pour fusionner les flux vidéo/audio (qualité 1080p), embarquer les métadonnées et les miniatures.

### Étape 4 — Lancer l'application

```bash
python3 main.py
```

---

## Désinstallation

### Si installé via le .deb

```bash
sudo apt remove tubor
```

### Si installé via le script ou manuellement

```bash
# Supprimer le raccourci
rm ~/.local/share/applications/tubor.desktop

# Supprimer la configuration (optionnel)
rm -rf ~/.config/tubor
```

---

## Dépannage

### PyQt6 introuvable

```bash
pip install --upgrade PyQt6
# ou
pip install --break-system-packages PyQt6
```

### yt-dlp introuvable ou erreurs de téléchargement

```bash
pip install --upgrade yt-dlp
# ou depuis l'application : Paramètres → Mettre à jour yt-dlp
```

### L'application ne démarre pas

```bash
# Vérifier Python 3.10+
python3 --version

# Vérifier les dépendances
python3 -c "import PyQt6; import yt_dlp; print('OK')"
```
