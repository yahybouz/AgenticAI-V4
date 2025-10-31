#!/bin/bash

# AgenticAI V4 - Test complet de toutes les fonctionnalités
# Ce script teste tous les endpoints et fonctionnalités disponibles

# Removed set -e to continue on errors

BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3001"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       AgenticAI V4 - Test Complet des Fonctionnalités     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

success_count=0
total_tests=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local auth_header="$5"

    total_tests=$((total_tests + 1))
    echo -e "${YELLOW}[Test $total_tests]${NC} $name..."

    if [ -z "$data" ]; then
        if [ -z "$auth_header" ]; then
            response=$(curl -s -X "$method" "$BASE_URL$endpoint" -w "\n%{http_code}")
        else
            response=$(curl -s -X "$method" "$BASE_URL$endpoint" -H "$auth_header" -w "\n%{http_code}")
        fi
    else
        if [ -z "$auth_header" ]; then
            response=$(curl -s -X "$method" "$BASE_URL$endpoint" -H "Content-Type: application/json" -d "$data" -w "\n%{http_code}")
        else
            response=$(curl -s -X "$method" "$BASE_URL$endpoint" -H "Content-Type: application/json" -H "$auth_header" -d "$data" -w "\n%{http_code}")
        fi
    fi

    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    if [[ "$http_code" =~ ^2[0-9]{2}$ ]]; then
        echo -e "${GREEN}✅${NC} OK (HTTP $http_code)"
        success_count=$((success_count + 1))
        return 0
    else
        echo -e "${RED}❌${NC} FAILED (HTTP $http_code)"
        echo "   Response: $body"
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Tests Basiques (sans authentification)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Root endpoint" "GET" "/"
test_endpoint "Health check" "GET" "/health"
test_endpoint "System info" "GET" "/info"
test_endpoint "OpenAPI docs" "GET" "/docs"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Authentification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test login
login_response=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@agenticai.dev","password":"admin123"}')

if echo "$login_response" | grep -q "access_token"; then
    echo -e "${GREEN}✅${NC} Login réussi"
    success_count=$((success_count + 1))
    total_tests=$((total_tests + 1))

    TOKEN=$(echo "$login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "   Token: ${TOKEN:0:50}..."
    AUTH_HEADER="Authorization: Bearer $TOKEN"
else
    echo -e "${RED}❌${NC} Login échoué"
    total_tests=$((total_tests + 1))
    echo "   Response: $login_response"
    TOKEN=""
    AUTH_HEADER=""
fi

# Test route protégée
test_endpoint "Get current user (/api/auth/me)" "GET" "/api/auth/me" "" "$AUTH_HEADER"

# Test register (création d'un nouvel utilisateur)
random_email="test_$(date +%s)@example.com"
register_data="{\"email\":\"$random_email\",\"password\":\"testpass123\",\"username\":\"testuser\"}"
test_endpoint "Register new user" "POST" "/api/auth/register" "$register_data"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Gestion des Utilisateurs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Get user stats" "GET" "/api/auth/me/stats" "" "$AUTH_HEADER"
test_endpoint "Generate API key" "POST" "/api/auth/me/api-key" "" "$AUTH_HEADER"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. Agents"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "List agents" "GET" "/api/agents/" "" "$AUTH_HEADER"

# Test création d'agent
agent_data='{"name":"TestAgent","domain":"chat","model":"qwen2.5:14b","skills":["chat"],"description":"Agent de test"}'
test_endpoint "Create agent" "POST" "/api/agents/" "$agent_data" "$AUTH_HEADER"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Orchestrateur"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Get orchestrator policy" "GET" "/api/orchestrator/policy" "" "$AUTH_HEADER"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. Documents & RAG (si Qdrant disponible)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Get document formats" "GET" "/api/documents/formats" "" "$AUTH_HEADER"
test_endpoint "Get cache stats" "GET" "/api/documents/cache/stats" "" "$AUTH_HEADER"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. Monitoring"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Get monitoring insights" "GET" "/api/monitoring/insights" "" "$AUTH_HEADER"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. Frontend (interface web)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if curl -s "$FRONTEND_URL" >/dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Frontend accessible sur $FRONTEND_URL"
    success_count=$((success_count + 1))
    total_tests=$((total_tests + 1))
else
    echo -e "${RED}❌${NC} Frontend non accessible"
    total_tests=$((total_tests + 1))
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  RÉSUMÉ DES TESTS                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

percentage=$((success_count * 100 / total_tests))

if [ $success_count -eq $total_tests ]; then
    echo -e "${GREEN}✅ Tous les tests ont réussi !${NC}"
else
    echo -e "${YELLOW}⚠️  Certains tests ont échoué${NC}"
fi

echo ""
echo "Tests réussis : $success_count / $total_tests ($percentage%)"
echo ""

if [ $percentage -ge 80 ]; then
    echo -e "${GREEN}🎉 Application opérationnelle à $percentage% !${NC}"
elif [ $percentage -ge 50 ]; then
    echo -e "${YELLOW}⚠️  Application partiellement opérationnelle ($percentage%)${NC}"
else
    echo -e "${RED}❌ Application nécessite des corrections ($percentage%)${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Services actifs :"
echo "  Backend:  $BASE_URL"
echo "  Frontend: $FRONTEND_URL"
echo "  API Docs: $BASE_URL/docs"
echo ""
echo "Connexion par défaut :"
echo "  Email:    admin@agenticai.dev"
echo "  Password: admin123"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit 0
