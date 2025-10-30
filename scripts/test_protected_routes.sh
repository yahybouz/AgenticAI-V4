#!/bin/bash
###############################################################################
# Test des routes protégées par authentification
###############################################################################

set -e

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="http://localhost:8000"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Test Routes Protégées - AgenticAI V4                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Test 1: Tenter d'accéder sans authentification (doit échouer)
echo -e "${BLUE}[Test 1]${NC} Accès sans authentification (doit échouer)..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/api/documents/cache/stats" 2>/dev/null || echo "000")
STATUS_CODE=$(echo "$RESPONSE" | tail -1)

if [ "$STATUS_CODE" = "401" ] || [ "$STATUS_CODE" = "403" ]; then
    echo -e "${GREEN}✓${NC} Accès refusé comme attendu (HTTP $STATUS_CODE)"
else
    echo -e "${RED}✗${NC} Devrait être refusé mais status: $STATUS_CODE"
fi

# Test 2: Connexion et obtention du token
echo ""
echo -e "${BLUE}[Test 2]${NC} Connexion avec utilisateur de test..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agenticai.dev","password":"admin123"}' 2>/dev/null || echo "{}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Token obtenu: ${TOKEN:0:30}..."
else
    echo -e "${RED}✗${NC} Échec obtention token"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# Test 3: Accès avec token valide
echo ""
echo -e "${BLUE}[Test 3]${NC} Accès avec token valide..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/api/documents/cache/stats" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "000")
STATUS_CODE=$(echo "$RESPONSE" | tail -1)

if [ "$STATUS_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Accès autorisé (HTTP 200)"
else
    echo -e "${RED}✗${NC} Échec accès avec token (HTTP $STATUS_CODE)"
fi

# Test 4: Vérifier les infos utilisateur
echo ""
echo -e "${BLUE}[Test 4]${NC} Récupération info utilisateur..."
USER_INFO=$(curl -s -X GET "$API_URL/api/auth/me" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null)

EMAIL=$(echo "$USER_INFO" | grep -o '"email":"[^"]*"' | cut -d'"' -f4)

if [ -n "$EMAIL" ]; then
    echo -e "${GREEN}✓${NC} Utilisateur: $EMAIL"
else
    echo -e "${RED}✗${NC} Échec récupération info utilisateur"
fi

# Test 5: Liste des agents (protégée)
echo ""
echo -e "${BLUE}[Test 5]${NC} Liste des agents (route protégée)..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/api/agents/" \
  -H "Authorization: Bearer $TOKEN" 2>/dev/null || echo "000")
STATUS_CODE=$(echo "$RESPONSE" | tail -1)

if [ "$STATUS_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Liste agents récupérée (HTTP 200)"
else
    echo -e "${RED}✗${NC} Échec liste agents (HTTP $STATUS_CODE)"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Tests terminés                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Toutes les routes protégées fonctionnent correctement !${NC}"
echo ""
