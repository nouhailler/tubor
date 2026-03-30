#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
#  Tubor — Script de construction du paquet Debian (.deb)
# ──────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"
PKG_NAME="tubor_${VERSION}_all"
BUILD_DIR="$SCRIPT_DIR/build/$PKG_NAME"

echo "╔══════════════════════════════════════════╗"
echo "║     Construction du paquet Tubor .deb    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Vérifier dpkg-deb ───────────────────────────────────────
if ! command -v dpkg-deb &>/dev/null; then
    echo "❌  dpkg-deb est requis. Installez-le avec : sudo apt install dpkg"
    exit 1
fi

# ── Nettoyer le build précédent ──────────────────────────────
rm -rf "$SCRIPT_DIR/build"
mkdir -p "$BUILD_DIR"

# ── Copier la structure Debian ───────────────────────────────
echo "→  Copie de la structure du paquet…"
cp -r "$SCRIPT_DIR/debian/." "$BUILD_DIR/"

# ── Copier les fichiers de l'application ─────────────────────
echo "→  Copie des fichiers de l'application…"
APP_DEST="$BUILD_DIR/usr/lib/tubor"

cp "$ROOT_DIR/main.py"          "$APP_DEST/"
cp "$ROOT_DIR/requirements.txt" "$APP_DEST/"

# Modules core/
cp "$ROOT_DIR/core/__init__.py"    "$APP_DEST/core/"
cp "$ROOT_DIR/core/config.py"      "$APP_DEST/core/"
cp "$ROOT_DIR/core/downloader.py"  "$APP_DEST/core/"
cp "$ROOT_DIR/core/utils.py"       "$APP_DEST/core/"

# Modules ui/
cp "$ROOT_DIR/ui/__init__.py"          "$APP_DEST/ui/"
cp "$ROOT_DIR/ui/main_window.py"       "$APP_DEST/ui/"
cp "$ROOT_DIR/ui/settings_dialog.py"   "$APP_DEST/ui/"
cp "$ROOT_DIR/ui/download_item.py"     "$APP_DEST/ui/"
cp "$ROOT_DIR/ui/help_dialog.py"       "$APP_DEST/ui/"
cp "$ROOT_DIR/ui/styles.py"            "$APP_DEST/ui/"

# ── Icône de l'application ───────────────────────────────────
echo "→  Copie de l'icône…"
if [ -f "$ROOT_DIR/screenshots/tubor-main.png" ]; then
    cp "$ROOT_DIR/screenshots/tubor-main.png" \
       "$BUILD_DIR/usr/share/pixmaps/tubor.png"
fi

# ── Permissions ──────────────────────────────────────────────
echo "→  Réglage des permissions…"
# D'abord les répertoires (pour permettre l'accès)
find "$BUILD_DIR" -type d -exec chmod 755 {} \;
# Ensuite les fichiers
find "$BUILD_DIR/usr/lib/tubor" -type f -exec chmod 644 {} \;
chmod 755 "$BUILD_DIR/DEBIAN/postinst"
chmod 755 "$BUILD_DIR/usr/bin/tubor"
chmod 644 "$BUILD_DIR/usr/share/applications/tubor.desktop"
[ -f "$BUILD_DIR/usr/share/pixmaps/tubor.png" ] && \
    chmod 644 "$BUILD_DIR/usr/share/pixmaps/tubor.png"

# ── Calculer la taille installée ─────────────────────────────
INSTALLED_SIZE=$(du -sk "$BUILD_DIR/usr" | cut -f1)
sed -i "s/^Installed-Size:.*/Installed-Size: $INSTALLED_SIZE/" \
    "$BUILD_DIR/DEBIAN/control"

# ── Construire le .deb ───────────────────────────────────────
echo "→  Construction du paquet .deb…"
OUTPUT_DEB="$SCRIPT_DIR/${PKG_NAME}.deb"
dpkg-deb --build --root-owner-group "$BUILD_DIR" "$OUTPUT_DEB"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅  Paquet construit avec succès !      ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Fichier : $OUTPUT_DEB"
echo "  Taille  : $(du -sh "$OUTPUT_DEB" | cut -f1)"
echo ""
echo "  Installer avec :"
echo "    sudo dpkg -i $OUTPUT_DEB"
echo "    sudo apt-get install -f   # résoudre les dépendances"
echo ""
