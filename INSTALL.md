# 📦 Guide d'installation — Tubor v0.3.0

## Installation via le paquet Debian (recommandé)

### Prérequis

```bash
sudo apt install python3 python3-venv nodejs npm ffmpeg
```

### Installer le .deb

```bash
# Télécharger
wget https://github.com/nouhailler/tubor/releases/latest/download/tubor_0.3.0_all.deb

# Installer
sudo dpkg -i tubor_0.3.0_all.deb

# Si des dépendances manquent
sudo apt-get install -f
```

### Lancer

```bash
tubor
```

Ou cherchez **Tubor** dans le menu de votre bureau (GNOME, KDE, XFCE…).

L'interface s'ouvre dans votre navigateur à **http://localhost:5173**.

---

## Installation depuis les sources

### 1. Cloner le dépôt

```bash
git clone https://github.com/nouhailler/tubor.git
cd tubor
```

### 2. Lancer

```bash
chmod +x start.sh
./start.sh
```

Le script installe automatiquement les dépendances Python (venv) et Node.js
au premier lancement, puis démarre le backend et le frontend.

---

## Désinstallation

```bash
# Si installé via .deb
sudo dpkg -r tubor

# Supprimer la configuration (optionnel)
rm -rf ~/.config/tubor
```

---

## Vérification de l'installation

```bash
# Backend accessible
curl http://localhost:8000/docs

# Frontend accessible
curl http://localhost:5173
```

---

## Problèmes fréquents

| Problème | Solution |
|----------|----------|
| `nodejs : Depends: ... but is not installable` | `sudo apt install nodejs npm` ou installer via [nvm](https://github.com/nvm-sh/nvm) |
| Port 5173 ou 8000 déjà utilisé | `fuser -k 5173/tcp 8000/tcp` puis relancer |
| ffmpeg manquant | `sudo apt install ffmpeg` |
| Permission denied sur start.sh | `chmod +x start.sh` |

---

## Construire le paquet .deb soi-même

```bash
chmod +x packaging/build_deb.sh
./packaging/build_deb.sh
# → dist/tubor_0.3.0_all.deb
```
