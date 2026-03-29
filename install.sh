#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  Tubor — Script d'installation (Linux)
# ──────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="tubor"

echo "╔══════════════════════════════════════╗"
echo "║     Installation de Tubor            ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Python 3.10+ ────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "❌  Python3 n'est pas installé. Installez-le d'abord."
    exit 1
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✔  Python $PY_VERSION détecté."

# ── ffmpeg ───────────────────────────────────────────────────
if ! command -v ffmpeg &>/dev/null; then
    echo ""
    echo "⚠  ffmpeg n'est pas installé."
    echo "   Pour l'installer :"
    echo "   Ubuntu/Debian : sudo apt install ffmpeg"
    echo "   Fedora        : sudo dnf install ffmpeg"
    echo "   Arch          : sudo pacman -S ffmpeg"
    echo ""
else
    FFMPEG_VER=$(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')
    echo "✔  ffmpeg $FFMPEG_VER détecté."
fi

# ── Dépendances Python ────────────────────────────────────────
echo ""
echo "→  Installation des dépendances Python…"
pip3 install --break-system-packages -r "$SCRIPT_DIR/requirements.txt" || \
    pip3 install --user -r "$SCRIPT_DIR/requirements.txt"
echo "✔  Dépendances installées."

# ── Fichier .desktop ──────────────────────────────────────────
DESKTOP_FILE="$HOME/.local/share/applications/tubor.desktop"
mkdir -p "$HOME/.local/share/applications"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Tubor
Comment=Téléchargeur vidéo & audio (yt-dlp GUI)
Exec=python3 $SCRIPT_DIR/main.py
Icon=folder-download
Terminal=false
Categories=Network;FileTransfer;GTK;
Keywords=youtube;video;download;yt-dlp;
EOF

echo "✔  Raccourci bureau créé : $DESKTOP_FILE"

# ── Lancer l'application ──────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════╗"
echo "║  ✅  Tubor installé avec succès !    ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  Lancer avec : python3 $SCRIPT_DIR/main.py"
echo "  Ou via le menu des applications (cherchez « Tubor »)"
echo ""
