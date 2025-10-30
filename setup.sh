#!/bin/bash
###############################################################################
# AgenticAI V4 - Script d'installation
# Installe toutes les dépendances nécessaires pour exécuter l'application
###############################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         AgenticAI V4 - Installation Setup                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

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

# Détecter l'OS
OS="$(uname -s)"
log_info "Système d'exploitation détecté: $OS"

###############################################################################
# 1. Vérifier et installer Homebrew (macOS)
###############################################################################
if [[ "$OS" == "Darwin" ]]; then
    log_info "Vérification de Homebrew..."
    if ! command_exists brew; then
        log_warning "Homebrew n'est pas installé. Installation en cours..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        log_success "Homebrew installé avec succès"
    else
        log_success "Homebrew déjà installé ($(brew --version | head -1))"
    fi
fi

###############################################################################
# 2. Vérifier et installer Python 3.11+
###############################################################################
log_info "Vérification de Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    log_success "Python installé: $PYTHON_VERSION"

    # Vérifier que la version est >= 3.11
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 11 ]]; then
        log_warning "Python 3.11+ requis. Installation en cours..."
        if [[ "$OS" == "Darwin" ]]; then
            brew install python@3.11
        else
            log_error "Veuillez installer Python 3.11+ manuellement"
            exit 1
        fi
    fi
else
    log_warning "Python non trouvé. Installation en cours..."
    if [[ "$OS" == "Darwin" ]]; then
        brew install python@3.11
    else
        log_error "Veuillez installer Python 3.11+ manuellement"
        exit 1
    fi
fi

###############################################################################
# 3. Vérifier et installer Docker
###############################################################################
log_info "Vérification de Docker..."
if ! command_exists docker; then
    log_warning "Docker n'est pas installé."
    if [[ "$OS" == "Darwin" ]]; then
        log_info "Installation de Docker Desktop pour macOS..."
        brew install --cask docker
        log_success "Docker installé. Veuillez démarrer Docker Desktop manuellement."
        log_warning "Une fois Docker Desktop démarré, relancez ce script."
        exit 0
    else
        log_error "Veuillez installer Docker manuellement depuis https://docs.docker.com/get-docker/"
        exit 1
    fi
else
    log_success "Docker installé ($(docker --version))"

    # Vérifier que Docker est en cours d'exécution
    if ! docker info >/dev/null 2>&1; then
        log_warning "Docker n'est pas en cours d'exécution."
        if [[ "$OS" == "Darwin" ]]; then
            log_info "Démarrage de Docker Desktop..."
            open -a Docker
            log_info "Attente du démarrage de Docker (30 secondes)..."
            sleep 30
        else
            log_error "Veuillez démarrer Docker manuellement"
            exit 1
        fi
    fi
fi

###############################################################################
# 4. Vérifier et installer Docker Compose
###############################################################################
log_info "Vérification de Docker Compose..."
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    log_warning "Docker Compose non trouvé. Installation..."
    if [[ "$OS" == "Darwin" ]]; then
        brew install docker-compose
    else
        log_error "Veuillez installer Docker Compose manuellement"
        exit 1
    fi
else
    if docker compose version >/dev/null 2>&1; then
        log_success "Docker Compose (plugin) installé"
    else
        log_success "Docker Compose installé ($(docker-compose --version))"
    fi
fi

###############################################################################
# 5. Vérifier et installer Ollama
###############################################################################
log_info "Vérification d'Ollama..."
if ! command_exists ollama; then
    log_warning "Ollama n'est pas installé. Installation en cours..."
    if [[ "$OS" == "Darwin" ]]; then
        brew install ollama
        log_success "Ollama installé"
    else
        log_info "Installation d'Ollama via curl..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
else
    log_success "Ollama déjà installé ($(ollama --version 2>&1 || echo 'version inconnue'))"
fi

# Démarrer Ollama si ce n'est pas déjà fait
log_info "Vérification du service Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    log_info "Démarrage d'Ollama..."
    if [[ "$OS" == "Darwin" ]]; then
        brew services start ollama
    else
        ollama serve &
    fi
    sleep 3
    log_success "Ollama démarré"
else
    log_success "Ollama est déjà en cours d'exécution"
fi

# Vérifier les modèles requis
log_info "Vérification des modèles Ollama..."
REQUIRED_MODELS=("qwen2.5:14b" "nomic-embed-text")

for model in "${REQUIRED_MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        log_success "Modèle $model déjà téléchargé"
    else
        log_warning "Modèle $model non trouvé. Téléchargement..."
        ollama pull "$model"
        log_success "Modèle $model téléchargé"
    fi
done

###############################################################################
# 6. Créer l'environnement virtuel Python
###############################################################################
log_info "Configuration de l'environnement virtuel Python..."

if [ ! -d ".venv" ]; then
    log_info "Création de l'environnement virtuel..."
    python3 -m venv .venv
    log_success "Environnement virtuel créé"
else
    log_success "Environnement virtuel déjà existant"
fi

# Activer l'environnement virtuel et installer les dépendances
log_info "Installation des dépendances Python..."
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e backend/
log_success "Dépendances Python installées"

###############################################################################
# 7. Créer le fichier .env si nécessaire
###############################################################################
log_info "Configuration des variables d'environnement..."

if [ ! -f "backend/.env" ]; then
    log_info "Création du fichier .env..."
    cat > backend/.env << EOF
# AgenticAI V4 Configuration
APP_NAME=AgenticAI
APP_VERSION=4.0.0
ENVIRONMENT=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_GRPC_PORT=6334
QDRANT_COLLECTION=documents

# Database Configuration (PostgreSQL)
DATABASE_URL=postgresql://agenticai:password@localhost:5432/agenticai

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
EOF
    log_success "Fichier .env créé"
else
    log_success "Fichier .env déjà existant"
fi

###############################################################################
# 8. Vérifier la structure des dossiers
###############################################################################
log_info "Vérification de la structure des dossiers..."
mkdir -p data/qdrant data/postgres logs
log_success "Structure des dossiers vérifiée"

###############################################################################
# Résumé de l'installation
###############################################################################
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Installation terminée avec succès !               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
log_success "Toutes les dépendances sont installées"
echo ""
echo -e "${BLUE}Composants installés :${NC}"
echo "  • Python $(python3 --version | awk '{print $2}')"
echo "  • Docker $(docker --version | awk '{print $3}' | tr -d ',')"
echo "  • Ollama"
echo "  • Modèles : qwen2.5:14b, nomic-embed-text"
echo ""
echo -e "${YELLOW}Prochaine étape :${NC}"
echo "  Lancez l'application avec: ${GREEN}./run.sh${NC}"
echo ""
