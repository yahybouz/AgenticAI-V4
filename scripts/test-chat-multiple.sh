#!/bin/bash

# Test multiple messages du chat

echo "=== Test Chat - Messages Multiples ==="
echo ""

# Login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agenticai.dev","password":"admin123"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Test différents messages
messages=(
    "Bonjour"
    "Qui es-tu ?"
    "Comment puis-je t'utiliser ?"
    "Parle-moi des agents"
    "Merci"
)

for msg in "${messages[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Message: $msg"
    echo ""

    RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat/send \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"content\":\"$msg\",\"context\":{}}")

    echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Agent: {d[\"agent_used\"]}\nRéponse: {d[\"message\"][:200]}...' if len(d['message']) > 200 else f'Agent: {d[\"agent_used\"]}\nRéponse: {d[\"message\"]}')"
    echo ""
done

echo "✅ Tests terminés !"
