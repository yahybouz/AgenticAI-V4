#!/bin/bash
###############################################################################
# AgenticAI V4 - Script de lancement
# Lance tous les services nécessaires pour exécuter l'application
###############################################################################

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Fonction pour vérifier si un port est utilisé
port_in_use() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Fonction de nettoyage en cas d'arrêt
cleanup() {
    echo ""
    log_warning "Arrêt en cours..."

    # Arrêter le backend si en cours
    if [ ! -z "$BACKEND_PID" ]; then
        log_info "Arrêt du backend..."
        kill $BACKEND_PID 2>/dev/null || true
    fi

    log_success "Arrêt terminé"
    exit 0
}

trap cleanup SIGINT SIGTERM

###############################################################################
# Banner
###############################################################################
clear
echo -e "${CYAN}"
cat << "EOF"
    ___                  __  _      ___    ____  _    ______
   /   | ____ ____  ____/ /_(_)____/   |  /  _/ | |  / / // /
  / /| |/ __ `/ _ \/ __  / / / ___/ /| |  / / | | / / // /_
 / ___ / /_/ /  __/ /_/ / / / /__/ ___ |_/ /  | |/ /__  __/
/_/  |_\__, /\___/\__,_/_/_/\___/_/  |_/___/  |___/  /_/
      /____/
EOF
echo -e "${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Multi-Agent AI System - Local Deployment          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

###############################################################################
# Vérifications préalables
###############################################################################
log_info "Vérifications préalables..."

# Vérifier si setup.sh a été exécuté
if [ ! -d ".venv" ] || [ ! -f "backend/.env" ]; then
    log_error "Installation incomplète détectée"
    echo ""
    echo -e "${YELLOW}Veuillez d'abord exécuter le script d'installation :${NC}"
    echo -e "  ${GREEN}./setup.sh${NC}"
    echo ""
    exit 1
fi

# Vérifier Docker
if ! command_exists docker; then
    log_error "Docker n'est pas installé"
    echo "Exécutez: ./setup.sh"
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    log_error "Docker n'est pas en cours d'exécution"
    echo "Démarrez Docker Desktop et réessayez"
    exit 1
fi

log_success "Vérifications préalables OK"

###############################################################################
# 1. Démarrer Ollama
###############################################################################
log_info "Vérification d'Ollama..."

if ! command_exists ollama; then
    log_error "Ollama n'est pas installé. Exécutez: ./setup.sh"
    exit 1
fi

# Vérifier si Ollama est en cours d'exécution
if ! pgrep -x "ollama" > /dev/null; then
    log_info "Démarrage d'Ollama..."
    OS="$(uname -s)"
    if [[ "$OS" == "Darwin" ]]; then
        brew services start ollama
    else
        ollama serve &
    fi
    sleep 3
fi

# Vérifier la connexion à Ollama
if curl -s http://localhost:11434/api/tags >/dev/null; then
    log_success "Ollama en cours d'exécution (http://localhost:11434)"
else
    log_error "Impossible de se connecter à Ollama"
    exit 1
fi

###############################################################################
# 2. Démarrer les services Docker (Qdrant, PostgreSQL, Redis)
###############################################################################
log_info "Démarrage des services Docker..."

if [ -f "docker-compose.yml" ]; then
    # Vérifier si les conteneurs sont déjà en cours d'exécution
    if docker compose ps | grep -q "Up"; then
        log_info "Services Docker déjà en cours d'exécution"
    else
        log_info "Lancement de Docker Compose..."
        docker compose up -d

        # Attendre que les services soient prêts
        log_info "Attente du démarrage des services (15 secondes)..."
        sleep 15
    fi

    log_success "Services Docker démarrés"

    # Afficher l'état des services
    echo ""
    docker compose ps
    echo ""
else
    log_warning "docker-compose.yml non trouvé, les services Docker ne seront pas démarrés"
fi

###############################################################################
# 3. Vérifier les ports
###############################################################################
log_info "Vérification des ports..."

PORTS=(
    "6333:Qdrant HTTP"
    "6334:Qdrant gRPC"
    "5432:PostgreSQL"
    "6379:Redis"
    "11434:Ollama"
)

for port_info in "${PORTS[@]}"; do
    IFS=':' read -r port service <<< "$port_info"
    if port_in_use "$port"; then
        log_success "$service sur le port $port"
    else
        log_warning "$service n'est pas accessible sur le port $port"
    fi
done

###############################################################################
# 4. Démarrer le backend FastAPI
###############################################################################
log_info "Démarrage du backend FastAPI..."

# Activer l'environnement virtuel
source .venv/bin/activate

# Vérifier si le port 8000 est libre
if port_in_use 8000; then
    log_warning "Le port 8000 est déjà utilisé"
    read -p "Voulez-vous arrêter le processus existant ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        log_error "Impossible de démarrer le backend"
        exit 1
    fi
fi

# Démarrer le backend en arrière-plan
log_info "Lancement d'uvicorn..."
cd backend
PYTHONPATH="/Users/yahybouz/Desktop/Mes Scripts/AgenticAI-V4/backend" \
    ../.venv/bin/uvicorn api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info &
BACKEND_PID=$!
cd ..

# Attendre que le backend soit prêt
log_info "Attente du démarrage du backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        log_success "Backend démarré sur http://localhost:8000"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
    log_error "Le backend n'a pas démarré correctement"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

###############################################################################
# Affichage du résumé
###############################################################################
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         AgenticAI V4 démarré avec succès !                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Services en cours d'exécution :${NC}"
echo ""
echo -e "  ${BLUE}API Backend:${NC}      http://localhost:8000"
echo -e "  ${BLUE}API Docs:${NC}         http://localhost:8000/docs"
echo -e "  ${BLUE}Qdrant Dashboard:${NC} http://localhost:6333/dashboard"
echo -e "  ${BLUE}Ollama:${NC}           http://localhost:11434"
echo ""
echo -e "${YELLOW}Endpoints disponibles :${NC}"
echo ""
echo -e "  • POST   /api/agents/execute       - Exécuter un agent"
echo -e "  • POST   /api/orchestrator/run     - Orchestration multi-agents"
echo -e "  • POST   /api/documents/upload     - Upload de documents"
echo -e "  • POST   /api/documents/search     - Recherche sémantique"
echo -e "  • GET    /api/cache/stats          - Statistiques du cache"
echo ""
echo -e "${CYAN}Logs du backend :${NC}"
echo -e "  Suivez les logs en temps réel avec: ${GREEN}tail -f backend/logs/app.log${NC}"
echo ""
echo -e "${YELLOW}Pour arrêter l'application :${NC}"
echo -e "  Appuyez sur ${GREEN}Ctrl+C${NC}"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Application en cours d'exécution - Appuyez sur Ctrl+C    ║${NC}"
echo -e "${BLUE}║  pour arrêter tous les services                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Garder le script en cours d'exécution et afficher les logs
tail -f backend/logs/*.log 2>/dev/null || wait $BACKEND_PID
