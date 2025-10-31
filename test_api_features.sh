#!/bin/bash
###############################################################################
# Test API Features - Agents, Documents, Stats
###############################################################################

echo "=== TEST API FEATURES ===="
echo ""

# Get token
echo "1. Login..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agenticai.dev","password":"admin123"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Token obtained"
echo ""

# Test Agents
echo "2. List agents..."
AGENTS=$(curl -s -X GET http://localhost:8000/api/agents/ \
  -H "Authorization: Bearer $TOKEN")

AGENT_COUNT=$(echo "$AGENTS" | grep -o '"id"' | wc -l)
echo "✅ Found $AGENT_COUNT agents"
echo ""

# Create custom agent
echo "3. Create custom agent..."
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/agents/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Agent API",
    "domain": "RAG",
    "skills": ["search", "analyze"],
    "description": "Agent créé via test automatique"
  }')

if echo "$CREATE_RESPONSE" | grep -q '"id"'; then
    AGENT_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "✅ Agent created with ID: $AGENT_ID"
else
    echo "❌ Failed to create agent"
    echo "$CREATE_RESPONSE"
fi
echo ""

# Test Stats
echo "4. Get user stats..."
STATS=$(curl -s -X GET http://localhost:8000/api/auth/stats \
  -H "Authorization: Bearer $TOKEN")

if echo "$STATS" | grep -q "agents_count"; then
    echo "✅ Stats retrieved"
    echo "$STATS"
else
    echo "❌ Failed to get stats"
fi
echo ""

# Test System Info
echo "5. Get system info..."
INFO=$(curl -s http://localhost:8000/info)
if echo "$INFO" | grep -q "agents"; then
    echo "✅ System info retrieved"
    echo "$INFO"
else
    echo "❌ Failed to get system info"
fi
echo ""

echo "========================================="
echo "✅ API Feature Tests Completed"
echo "========================================="
