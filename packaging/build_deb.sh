#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
#  Tubor — Script de construction du paquet Debian (.deb)
#  Usage : ./packaging/build_deb.sh
# ──────────────────────────────────────────────────────────────────
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="0.3.0"
PKG_NAME="tubor_${VERSION}_all"
DEB_ROOT="$ROOT_DIR/packaging/deb_root"
BUILD_DIR="$(mktemp -d)"
DIST_DIR="$ROOT_DIR/dist"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${CYAN}┌─────────────────────────────────────────┐${NC}"
echo -e "${CYAN}│   Tubor v${VERSION} — Build paquet .deb     │${NC}"
echo -e "${CYAN}└─────────────────────────────────────────┘${NC}"
echo ""

# ── 1. Préparer le répertoire de build ────────────────────────────
echo -e "${YELLOW}[1/5] Préparation du répertoire de build...${NC}"
PKG_DIR="$BUILD_DIR/$PKG_NAME"
mkdir -p "$PKG_DIR"

# Copier la structure DEBIAN
cp -r "$DEB_ROOT/DEBIAN" "$PKG_DIR/"
cp -r "$DEB_ROOT/usr"    "$PKG_DIR/"

# ── 2. Copier les fichiers de l'application ────────────────────────
echo -e "${YELLOW}[2/5] Copie des fichiers de l'application...${NC}"
mkdir -p "$PKG_DIR/opt/tubor"

rsync -a --exclude='.git' \
         --exclude='.claude' \
         --exclude='backend/.venv' \
         --exclude='frontend/node_modules' \
         --exclude='frontend/dist' \
         --exclude='packaging' \
         --exclude='dist' \
         --exclude='*.pyc' \
         --exclude='__pycache__' \
         "$ROOT_DIR/" "$PKG_DIR/opt/tubor/"

echo -e "${GREEN}   ✔ Fichiers copiés${NC}"

# ── 3. Permissions ────────────────────────────────────────────────
echo -e "${YELLOW}[3/5] Application des permissions...${NC}"
chmod 755 "$PKG_DIR/DEBIAN/postinst"
chmod 755 "$PKG_DIR/DEBIAN/prerm"
chmod 755 "$PKG_DIR/usr/bin/tubor"
chmod 755 "$PKG_DIR/opt/tubor/start.sh"
# Forcer la propriété root pour le .deb
find "$PKG_DIR" -exec chown root:root {} + 2>/dev/null || true
echo -e "${GREEN}   ✔ Permissions OK${NC}"

# ── 4. Construire le .deb ─────────────────────────────────────────
echo -e "${YELLOW}[4/5] Construction du paquet .deb...${NC}"
mkdir -p "$DIST_DIR"
dpkg-deb --build --root-owner-group "$PKG_DIR" "$DIST_DIR/${PKG_NAME}.deb"
echo -e "${GREEN}   ✔ Paquet construit${NC}"

# ── 5. Nettoyage ──────────────────────────────────────────────────
echo -e "${YELLOW}[5/5] Nettoyage...${NC}"
rm -rf "$BUILD_DIR"
echo -e "${GREEN}   ✔ Nettoyage OK${NC}"

echo ""
echo -e "${GREEN}┌─────────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  ✔ Paquet créé avec succès !                    │${NC}"
echo -e "${GREEN}│                                                 │${NC}"
echo -e "${GREEN}│  → dist/${PKG_NAME}.deb    │${NC}"
echo -e "${GREEN}│                                                 │${NC}"
echo -e "${GREEN}│  Installer :                                    │${NC}"
echo -e "${GREEN}│    sudo dpkg -i dist/${PKG_NAME}.deb   │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────────┘${NC}"
echo ""
