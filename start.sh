#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
#  Tubor v0.2 — Script de démarrage
#  Lance le backend FastAPI et le frontend Vite en parallèle
# ──────────────────────────────────────────────────────────

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}┌─────────────────────────────────────┐${NC}"
echo -e "${CYAN}│          Tubor v0.2 — Web           │${NC}"
echo -e "${CYAN}└─────────────────────────────────────┘${NC}"

# ── Vérifications préalables ────────────────────────────────

if ! command -v python3 &>/dev/null; then
  echo "❌  Python 3 est requis. Installez-le d'abord."
  exit 1
fi

if ! command -v node &>/dev/null; then
  echo "❌  Node.js est requis. Installez-le d'abord."
  exit 1
fi

# ── Installation des dépendances (si besoin) ────────────────

echo ""
echo -e "${YELLOW}[1/4] Vérification des dépendances Python…${NC}"
if [ ! -d "$BACKEND_DIR/.venv" ]; then
  echo "   → Création de l'environnement virtuel…"
  python3 -m venv "$BACKEND_DIR/.venv"
fi
source "$BACKEND_DIR/.venv/bin/activate"
pip install -q -r "$BACKEND_DIR/requirements.txt"
echo -e "${GREEN}   ✔ Dépendances Python OK${NC}"

echo ""
echo -e "${YELLOW}[2/4] Vérification des dépendances Node…${NC}"
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "   → Installation npm…"
  (cd "$FRONTEND_DIR" && npm install --silent)
fi
echo -e "${GREEN}   ✔ Dépendances Node OK${NC}"

# ── Lancement ───────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[3/4] Démarrage du backend FastAPI (port 8000)…${NC}"
(cd "$BACKEND_DIR" && source .venv/bin/activate && uvicorn main:app --host 127.0.0.1 --port 8000 --reload) &
BACKEND_PID=$!

sleep 1

echo ""
echo -e "${YELLOW}[4/4] Démarrage du frontend Vite (port 5173)…${NC}"
(cd "$FRONTEND_DIR" && npm run dev) &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  ✔ Tubor est lancé !                        │${NC}"
echo -e "${GREEN}│                                             │${NC}"
echo -e "${GREEN}│  Frontend : http://localhost:5173           │${NC}"
echo -e "${GREEN}│  API docs : http://localhost:8000/docs      │${NC}"
echo -e "${GREEN}│                                             │${NC}"
echo -e "${GREEN}│  Ctrl+C pour arrêter tous les services      │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────┘${NC}"
echo ""

# Arrête tout proprement à Ctrl+C
trap "echo ''; echo 'Arrêt en cours…'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

wait
