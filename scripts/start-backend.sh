#!/bin/bash

# Script pour démarrer le backend AgenticAI V4

cd "$(dirname "$0")/.."

echo "🚀 Démarrage du backend AgenticAI V4..."

# Arrêter les processus existants sur le port 8000
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️  Port 8000 occupé, arrêt du processus existant..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Démarrer le backend
echo "✅ Démarrage du serveur sur http://localhost:8000..."
cd backend
PYTHONPATH="$(pwd)" .venv/bin/python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
