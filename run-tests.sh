#!/bin/bash
###############################################################################
# Script de Test Complet - AgenticAI V4
# Teste tous les composants de l'application
###############################################################################

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         AgenticAI V4 - Tests Complets                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Cleanup des processus existants
echo -e "${YELLOW}[1/8]${NC} Nettoyage des processus existants..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅${NC} Ports libérés"
echo ""

# Test 1: Backend Initialization
echo -e "${YELLOW}[2/8]${NC} Test d'initialisation du backend..."
backend/.venv/bin/python test_startup.py > /tmp/startup_test.log 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅${NC} Backend initialization OK"
else
    echo -e "${RED}❌${NC} Backend initialization FAILED"
    cat /tmp/startup_test.log
    exit 1
fi
echo ""

# Test 2: Start Backend
echo -e "${YELLOW}[3/8]${NC} Démarrage du backend..."
cd backend
PYTHONPATH="$(pwd)" .venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 > /tmp/backend_test.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "   Backend PID: $BACKEND_PID"

# Wait for backend
for i in {1..30}; do
    if curl -s http://localhost:8000/ >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} Backend démarré sur port 8000"
        break
    fi
    sleep 1
done

if ! curl -s http://localhost:8000/ >/dev/null 2>&1; then
    echo -e "${RED}❌${NC} Backend failed to start"
    cat /tmp/backend_test.log | tail -50
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi
echo ""

# Test 3: Root Endpoint
echo -e "${YELLOW}[4/8]${NC} Test endpoint racine..."
RESPONSE=$(curl -s http://localhost:8000/)
if echo "$RESPONSE" | grep -q "AgenticAI V4"; then
    echo -e "${GREEN}✅${NC} Root endpoint OK"
else
    echo -e "${RED}❌${NC} Root endpoint FAILED"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 4: Health Check
echo -e "${YELLOW}[5/8]${NC} Test health check..."
HEALTH=$(curl -s http://localhost:8000/health)
if echo "$HEALTH" | grep -q "status"; then
    echo -e "${GREEN}✅${NC} Health check OK"
else
    echo -e "${RED}❌${NC} Health check FAILED"
fi
echo ""

# Test 5: Authentication - Login
echo -e "${YELLOW}[6/8]${NC} Test authentification (login admin)..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agenticai.dev","password":"admin123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$TOKEN" ]; then
    echo -e "${GREEN}✅${NC} Login OK - Token reçu"
    echo "   Token: ${TOKEN:0:50}..."
else
    echo -e "${RED}❌${NC} Login FAILED"
    echo "Response: $LOGIN_RESPONSE"
fi
echo ""

# Test 6: Protected Route - Get Current User
echo -e "${YELLOW}[7/8]${NC} Test route protégée (/api/auth/me)..."
if [ ! -z "$TOKEN" ]; then
    USER_RESPONSE=$(curl -s -X GET http://localhost:8000/api/auth/me \
      -H "Authorization: Bearer $TOKEN")

    if echo "$USER_RESPONSE" | grep -q "admin@agenticai.dev"; then
        echo -e "${GREEN}✅${NC} Route protégée OK - Utilisateur récupéré"
    else
        echo -e "${RED}❌${NC} Route protégée FAILED"
        echo "Response: $USER_RESPONSE"
    fi
else
    echo -e "${YELLOW}⏭${NC}  Test ignoré (pas de token)"
fi
echo ""

# Test 7: Frontend
echo -e "${YELLOW}[8/8]${NC} Vérification frontend..."
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✅${NC} Frontend dependencies installées"

    # Start frontend
    cd frontend
    npm run dev > /tmp/frontend_test.log 2>&1 &
    FRONTEND_PID=$!
    cd ..

    sleep 8

    if lsof -ti:3000 >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} Frontend démarré sur port 3000"
    else
        echo -e "${RED}❌${NC} Frontend failed to start"
        cat /tmp/frontend_test.log | tail -20
    fi
else
    echo -e "${YELLOW}⚠${NC}  Frontend dependencies non installées"
fi
echo ""

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  RÉSUMÉ DES TESTS                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Services Actifs:${NC}"
lsof -ti:8000 >/dev/null 2>&1 && echo -e "  ✅ Backend:  http://localhost:8000" || echo -e "  ❌ Backend"
lsof -ti:3000 >/dev/null 2>&1 && echo -e "  ✅ Frontend: http://localhost:3000" || echo -e "  ❌ Frontend"
echo ""
echo -e "${YELLOW}Connexion par défaut:${NC}"
echo -e "  Email:    ${GREEN}admin@agenticai.dev${NC}"
echo -e "  Password: ${GREEN}admin123${NC}"
echo ""
echo -e "${BLUE}Documentation API:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Pour arrêter les services:${NC}"
echo "  kill $BACKEND_PID"
[ ! -z "$FRONTEND_PID" ] && echo "  kill $FRONTEND_PID"
echo ""
echo -e "${GREEN}✅ Tests terminés avec succès !${NC}"
echo ""
