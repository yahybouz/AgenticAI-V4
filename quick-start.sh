#!/bin/bash
###############################################################################
# Quick Start Script - Lance Frontend + Backend sans dépendances Docker
# Utilise l'ancien système in-memory pour les tests rapides
###############################################################################

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         AgenticAI V4 - Quick Start (No Docker)            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Fonction cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}Arrêt des services...${NC}"
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Vérifier que les dépendances sont installées
if [ ! -d "backend/.venv" ]; then
    echo -e "${YELLOW}Installation des dépendances backend...${NC}"
    cd backend
    python3 -m venv .venv
    .venv/bin/pip install -e .
    cd ..
fi

if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installation des dépendances frontend...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Créer un backup temporaire et restaurer le service in-memory
echo -e "${BLUE}[INFO]${NC} Configuration du mode test (in-memory)..."

# Tuer les processus existants sur les ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Démarrer le backend
echo -e "${BLUE}[INFO]${NC} Démarrage du backend..."
cd backend
PYTHONPATH="$(pwd)" \
    .venv/bin/uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    > /tmp/backend_quick.log 2>&1 &
BACKEND_PID=$!
cd ..

# Attendre que le backend démarre
echo -e "${BLUE}[INFO]${NC} Attente du backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/ >/dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} Backend démarré"
        break
    fi
    sleep 1
done

# Démarrer le frontend
echo -e "${BLUE}[INFO]${NC} Démarrage du frontend..."
cd frontend
npm run dev > /tmp/frontend_quick.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 5

# Afficher le résumé
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         AgenticAI V4 - Prêt à l'emploi !                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🌐 Frontend:${NC}     http://localhost:3000"
echo -e "${BLUE}🔧 Backend API:${NC}  http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC}     http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Connexion par défaut:${NC}"
echo -e "  Email:    ${GREEN}admin@agenticai.dev${NC}"
echo -e "  Password: ${GREEN}admin123${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} Mode test sans PostgreSQL/Qdrant/Ollama"
echo -e "      Les données sont en mémoire (perdues au redémarrage)"
echo ""
echo -e "${YELLOW}Pour arrêter:${NC} Appuyez sur ${GREEN}Ctrl+C${NC}"
echo ""

# Ouvrir le navigateur automatiquement
if command -v open >/dev/null 2>&1; then
    echo -e "${BLUE}[INFO]${NC} Ouverture du navigateur..."
    sleep 2
    open http://localhost:3000
fi

# Attendre
echo -e "${BLUE}Application en cours d'exécution...${NC}"
wait $BACKEND_PID
