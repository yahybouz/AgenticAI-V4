#!/bin/bash
# AgenticAI V4 - Script de téléchargement des modèles Ollama
# Usage: ./scripts/download-models.sh

set -e

echo "🚀 AgenticAI V4 - Téléchargement des modèles Ollama"
echo "=================================================="

# Vérifier si Ollama est installé
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama n'est pas installé. Veuillez l'installer depuis https://ollama.ai"
    exit 1
fi

# Vérifier si Ollama est en cours d'exécution
if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "⚠️  Ollama ne semble pas être en cours d'exécution"
    echo "   Démarrage d'Ollama..."
    ollama serve &
    sleep 5
fi

echo ""
echo "📥 Téléchargement des modèles LLM..."
echo "-----------------------------------"

# LLM Principal
echo "1/7 - qwen2.5:14b (LLM principal, multilingue)"
ollama pull qwen2.5:14b

# LLM Rapide
echo "2/7 - phi4:latest (LLM rapide pour tâches simples)"
ollama pull phi4:latest

# LLM Code
echo "3/7 - qwen2.5-coder:7b (Génération de code)"
ollama pull qwen2.5-coder:7b

# Embeddings
echo ""
echo "📥 Téléchargement du modèle d'embeddings..."
echo "-----------------------------------"
echo "4/7 - nomic-embed-text:latest (Embeddings long context)"
ollama pull nomic-embed-text:latest

# Multimodal
echo ""
echo "📥 Téléchargement du modèle multimodal..."
echo "-----------------------------------"
echo "5/7 - llava:13b (Vision + Langage)"
ollama pull llava:13b

# ASR
echo ""
echo "📥 Téléchargement du modèle ASR..."
echo "-----------------------------------"
echo "6/7 - whisper:large-v3 (Transcription audio)"
if ollama list | grep -q "whisper:large-v3"; then
    echo "✅ whisper:large-v3 déjà installé"
else
    echo "⚠️  whisper:large-v3 n'est pas disponible via Ollama"
    echo "   Utilisez whisper localement ou via API externe"
fi

# Modèles alternatifs
echo ""
echo "📥 Modèles alternatifs (optionnels)..."
echo "-----------------------------------"
echo "7/7 - llama3.3:70b (Si vous avez beaucoup de RAM/VRAM)"
read -p "Télécharger llama3.3:70b? (très gros modèle) [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ollama pull llama3.3:70b
else
    echo "⏭️  Ignoré"
fi

echo ""
echo "✅ Téléchargement terminé!"
echo ""
echo "📋 Modèles installés:"
ollama list

echo ""
echo "🎉 Tous les modèles requis sont prêts!"
echo "   Vous pouvez maintenant démarrer AgenticAI V4"
echo ""
echo "Prochaines étapes:"
echo "  1. Vérifier la configuration: cat .env"
echo "  2. Démarrer les services: docker compose up -d"
echo "  3. Démarrer le backend: ./scripts/run-backend.sh"
