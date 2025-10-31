#!/bin/bash

# Test du chat endpoint

echo "=== Test Chat Endpoint ==="
echo ""

# Login
echo "1. Login..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agenticai.dev","password":"admin123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "✅ Token récupéré: ${TOKEN:0:50}..."
echo ""

# Send chat message
echo "2. Envoi message chat..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Bonjour, qui es-tu ?","context":{}}')

echo "Response:"
echo "$CHAT_RESPONSE" | python3 -m json.tool 2>&1 || echo "$CHAT_RESPONSE"
