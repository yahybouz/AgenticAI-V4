#!/bin/bash

###############################################################################
# NexusAI - Installation Automatique Complète
# The Connected Intelligence Platform
###############################################################################

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_header() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}🌟 $1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════${NC}\n"
}

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

###############################################################################
# Bannière
###############################################################################

clear
echo -e "${PURPLE}"
cat << "EOF"
    _   __                      ___    ____
   / | / /__  _  ____  _______/   |  /  _/
  /  |/ / _ \| |/_/ / / / ___/ /| |  / /
 / /|  /  __/>  </ /_/ (__  ) ___ |_/ /
/_/ |_/\___/_/|_|\__,_/____/_/  |_/___/

    The Connected Intelligence Platform
EOF
echo -e "${NC}\n"

print_header "INSTALLATION DE NEXUSAI"

###############################################################################
# 1. Vérification du système
###############################################################################

print_header "1. VÉRIFICATION DU SYSTÈME"

# Vérifier macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "Ce script nécessite macOS"
    exit 1
fi
print_success "macOS détecté"

# Vérifier l'espace disque (minimum 10 GB)
AVAILABLE_SPACE=$(df -g . | awk 'NR==2 {print $4}')
if [ "$AVAILABLE_SPACE" -lt 10 ]; then
    print_warning "Espace disque faible: ${AVAILABLE_SPACE}GB disponible"
    print_warning "Recommandé: 50GB minimum"
fi

print_success "Espace disque: ${AVAILABLE_SPACE}GB disponible"

###############################################################################
# 2. Installation de Homebrew
###############################################################################

print_header "2. HOMEBREW"

if ! command -v brew &> /dev/null; then
    print_step "Installation de Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    print_success "Homebrew installé"
else
    print_success "Homebrew déjà installé"
    brew --version
fi

###############################################################################
# 3. Installation de Python 3.11+
###############################################################################

print_header "3. PYTHON 3.11+"

if ! command -v python3 &> /dev/null; then
    print_step "Installation de Python 3.11..."
    brew install python@3.11
    print_success "Python installé"
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    print_success "Python $PYTHON_VERSION déjà installé"
fi

python3 --version

###############################################################################
# 4. Installation de Node.js et npm
###############################################################################

print_header "4. NODE.JS & NPM"

if ! command -v node &> /dev/null; then
    print_step "Installation de Node.js..."
    brew install node
    print_success "Node.js installé"
else
    print_success "Node.js déjà installé"
fi

node --version
npm --version

###############################################################################
# 5. Installation de Ollama
###############################################################################

print_header "5. OLLAMA (LLM Local)"

if ! command -v ollama &> /dev/null; then
    print_step "Installation de Ollama..."
    brew install ollama
    print_success "Ollama installé"
else
    print_success "Ollama déjà installé"
fi

ollama --version

# Démarrer Ollama en arrière-plan
print_step "Démarrage du service Ollama..."
brew services start ollama 2>/dev/null || true
sleep 3
print_success "Service Ollama démarré"

###############################################################################
# 6. Téléchargement des modèles Ollama
###############################################################################

print_header "6. MODÈLES OLLAMA"

print_step "Téléchargement du modèle principal: qwen2.5:14b (9.0 GB)"
print_warning "Cela peut prendre 10-30 minutes selon votre connexion..."
ollama pull qwen2.5:14b

print_step "Téléchargement du modèle embeddings: nomic-embed-text (274 MB)"
ollama pull nomic-embed-text

print_success "Modèles téléchargés"
ollama list

###############################################################################
# 7. Installation Docker (optionnel)
###############################################################################

print_header "7. DOCKER (Optionnel)"

if ! command -v docker &> /dev/null; then
    print_warning "Docker Desktop non installé"
    echo -e "   Pour PostgreSQL/Qdrant/Redis, installer Docker Desktop:"
    echo -e "   ${CYAN}https://www.docker.com/products/docker-desktop${NC}"
    echo ""
    read -p "   Installer Docker maintenant? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        brew install --cask docker
        print_success "Docker Desktop installé"
        print_warning "Lancez Docker Desktop manuellement avant de continuer"
        read -p "   Appuyez sur Entrée quand Docker est démarré..."
    else
        print_warning "Docker ignoré - Le système utilisera SQLite"
    fi
else
    print_success "Docker déjà installé"
    docker --version
fi

###############################################################################
# 8. Configuration Backend Python
###############################################################################

print_header "8. BACKEND PYTHON"

cd "$(dirname "$0")"
PROJECT_ROOT=$(pwd)

print_step "Création de l'environnement virtuel Python..."
cd backend
python3 -m venv .venv
print_success "Environnement virtuel créé"

print_step "Installation des dépendances Python..."
.venv/bin/pip install --upgrade pip setuptools wheel
.venv/bin/pip install -r requirements.txt
print_success "Dépendances Python installées"

# Créer le fichier .env si nécessaire
if [ ! -f .env ]; then
    print_step "Création du fichier .env..."
    cat > .env << 'ENVFILE'
# NexusAI Configuration
DATABASE_URL=sqlite+aiosqlite:///./agenticai.db
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_DAYS=7
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:14b
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
ENVFILE
    print_success "Fichier .env créé"
fi

cd "$PROJECT_ROOT"

###############################################################################
# 9. Configuration Frontend React
###############################################################################

print_header "9. FRONTEND REACT"

cd frontend

print_step "Installation des dépendances npm..."
npm install
print_success "Dépendances npm installées"

# Créer le fichier .env si nécessaire
if [ ! -f .env ]; then
    print_step "Création du fichier .env frontend..."
    cat > .env << 'ENVFILE'
VITE_API_BASE_URL=http://localhost:8000
ENVFILE
    print_success "Fichier .env frontend créé"
fi

cd "$PROJECT_ROOT"

###############################################################################
# 10. Initialisation de la base de données
###############################################################################

print_header "10. BASE DE DONNÉES"

print_step "Initialisation de la base SQLite..."
# La DB sera créée automatiquement au premier démarrage
print_success "Base de données prête (SQLite)"

###############################################################################
# 11. Services Docker (optionnel)
###############################################################################

if command -v docker &> /dev/null; then
    print_header "11. SERVICES DOCKER (Optionnel)"

    if [ -f docker-compose.yml ]; then
        read -p "   Démarrer PostgreSQL/Qdrant/Redis avec Docker? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_step "Démarrage des services Docker..."
            docker compose up -d
            print_success "Services Docker démarrés"
            docker compose ps
        else
            print_warning "Services Docker ignorés - Utilisation de SQLite"
        fi
    fi
fi

###############################################################################
# 12. Création des scripts de lancement
###############################################################################

print_header "12. SCRIPTS DE LANCEMENT"

# Script start.sh
cat > start.sh << 'STARTSCRIPT'
#!/bin/bash

# NexusAI - Démarrage rapide

echo "🌟 Démarrage de NexusAI..."

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt de NexusAI..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Démarrer backend
echo "▶ Démarrage backend sur http://localhost:8000..."
cd "$PROJECT_ROOT"
PYTHONPATH="$PROJECT_ROOT/backend" backend/.venv/bin/python backend/api/main.py &
BACKEND_PID=$!

# Attendre 5 secondes
sleep 5

# Démarrer frontend
echo "▶ Démarrage frontend sur http://localhost:3001..."
cd "$PROJECT_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ NexusAI est démarré !"
echo ""
echo "   Frontend: http://localhost:3001"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "   Identifiants:"
echo "   Email:    admin@agenticai.dev"
echo "   Password: admin123"
echo ""
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""

# Attendre
wait
STARTSCRIPT

chmod +x start.sh
print_success "Script start.sh créé"

# Script stop.sh
cat > stop.sh << 'STOPSCRIPT'
#!/bin/bash

# NexusAI - Arrêt

echo "🛑 Arrêt de NexusAI..."

# Tuer les processus sur les ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ NexusAI arrêté"
STOPSCRIPT

chmod +x stop.sh
print_success "Script stop.sh créé"

###############################################################################
# 13. Test de l'installation
###############################################################################

print_header "13. TEST DE L'INSTALLATION"

print_step "Vérification de l'installation..."

# Vérifier Python
if backend/.venv/bin/python -c "import fastapi" 2>/dev/null; then
    print_success "Backend Python: OK"
else
    print_error "Backend Python: ERREUR"
fi

# Vérifier npm
if [ -d "frontend/node_modules" ]; then
    print_success "Frontend npm: OK"
else
    print_error "Frontend npm: ERREUR"
fi

# Vérifier Ollama
if ollama list | grep -q "qwen2.5:14b"; then
    print_success "Ollama modèle: OK"
else
    print_warning "Ollama modèle: Téléchargement en cours..."
fi

###############################################################################
# FIN DE L'INSTALLATION
###############################################################################

print_header "INSTALLATION TERMINÉE !"

echo -e "${GREEN}"
cat << "EOF"
    ✅ NexusAI est prêt !

    Pour démarrer l'application:

        ./start.sh

    Puis ouvrez votre navigateur:

        http://localhost:3001

    Identifiants:
        Email:    admin@agenticai.dev
        Password: admin123

    Documentation:
        http://localhost:8000/docs

    Pour arrêter:
        ./stop.sh
        (ou Ctrl+C dans le terminal)
EOF
echo -e "${NC}\n"

print_success "Installation complète !"
echo -e "\n${CYAN}Prochaines étapes:${NC}"
echo -e "  1. ${BLUE}./start.sh${NC}               - Démarrer NexusAI"
echo -e "  2. ${BLUE}open http://localhost:3001${NC} - Ouvrir dans le navigateur"
echo -e "  3. ${BLUE}./stop.sh${NC}                - Arrêter NexusAI"
echo -e ""
echo -e "${PURPLE}🌟 Enjoy your Connected Intelligence Platform! 🌟${NC}\n"
