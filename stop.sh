#!/bin/bash
###############################################################################
# AgenticAI V4 - Script d'arrêt
# Arrête proprement tous les services
###############################################################################

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         AgenticAI V4 - Arrêt des services                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Arrêter le backend FastAPI
log_info "Arrêt du backend FastAPI..."
if lsof -ti:8000 >/dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    log_success "Backend arrêté"
else
    log_warning "Backend non trouvé (port 8000 libre)"
fi

# 2. Arrêter Docker Compose
if [ -f "docker-compose.yml" ]; then
    log_info "Arrêt des services Docker..."
    docker compose down
    log_success "Services Docker arrêtés"
fi

# 3. Arrêter Ollama (optionnel)
read -p "Voulez-vous arrêter Ollama ? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    OS="$(uname -s)"
    if [[ "$OS" == "Darwin" ]]; then
        brew services stop ollama
        log_success "Ollama arrêté"
    else
        pkill -f "ollama serve"
        log_success "Ollama arrêté"
    fi
fi

echo ""
log_success "Tous les services ont été arrêtés"
echo ""
