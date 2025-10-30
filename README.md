# AgenticAI V4 🤖

**Système multi-agents local avec RAG alimenté par Ollama**

Assistant IA intelligent orchestrant plusieurs agents spécialisés pour des tâches complexes, avec support de documents multi-formats et recherche sémantique avancée.

## 🚀 Démarrage rapide

### Installation en une commande

```bash
./setup.sh
```

Ce script installe automatiquement :
- ✅ Homebrew (macOS)
- ✅ Python 3.11+
- ✅ Docker Desktop
- ✅ Ollama + modèles (`qwen2.5:14b`, `nomic-embed-text`)
- ✅ Environnement virtuel Python
- ✅ Toutes les dépendances backend

### Lancer l'application

```bash
./run.sh
```

Le script démarre automatiquement :
- Ollama (LLM local)
- Services Docker (Qdrant, PostgreSQL, Redis)
- Backend FastAPI

### Arrêter l'application

```bash
./stop.sh
# OU Ctrl+C dans le terminal de run.sh
```

## 📋 Prérequis

- macOS ou Linux
- 16 GB RAM minimum (32 GB recommandé)
- 50 GB d'espace disque libre

## ✨ Fonctionnalités

### Système multi-agents
- **Orchestrateur intelligent** - Coordination automatique
- **Coach personnel** - Habitudes, objectifs, motivation
- **Email** - Rédaction, analyse de sentiment
- **Voice** - Transcription, synthèse vocale
- **Project Manager** - Planification, suivi
- **Web Intelligence** - Recherche, analyse
- **Documentation** - Génération, analyse

### RAG enrichi
- **Multi-formats** - PDF, DOCX, TXT, Markdown, HTML
- **Recherche sémantique** - Embedding via nomic-embed-text
- **Cache LRU** - Optimisation des performances
- **Reranking LLM** - Meilleure pertinence

## 🔧 Utilisation

### API Documentation
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Upload de documents

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -F "file=@document.pdf" \
  -F "collection_name=documents"
```

### Recherche sémantique

```bash
curl -X POST "http://localhost:8000/api/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Comment fonctionne le RAG ?",
    "top_k": 5,
    "enable_reranking": true
  }'
```

### Orchestration multi-agents

```bash
curl -X POST "http://localhost:8000/api/orchestrator/run" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyse ce document et crée un résumé",
    "context": {}
  }'
```

## 🏗️ Architecture

```
AgenticAI-V4/
├── backend/
│   ├── agents/          # Agents spécialisés
│   ├── api/             # Routes FastAPI
│   ├── services/        # Services métier
│   └── models/          # Modèles Pydantic
├── scripts/             # Scripts utilitaires
├── setup.sh             # Installation
├── run.sh               # Lancement
└── stop.sh              # Arrêt
```

## 🛠️ Stack technique

- **Backend** : FastAPI (Python 3.11+)
- **LLM** : Ollama (qwen2.5:14b)
- **Vector DB** : Qdrant
- **Database** : PostgreSQL
- **Cache** : Redis
- **Docker** : Containerisation

## 📊 Services

Quand l'application est lancée :

| Service | URL | Description |
|---------|-----|-------------|
| **API Backend** | http://localhost:8000 | API REST principale |
| **API Docs** | http://localhost:8000/docs | Documentation interactive |
| **Qdrant** | http://localhost:6333/dashboard | Vector database |
| **Ollama** | http://localhost:11434 | LLM local |

## 🧪 Tests

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Tester le système RAG
python scripts/test_enhanced_rag.py
```

## 🐛 Troubleshooting

### Ollama ne démarre pas
```bash
brew services restart ollama  # macOS
```

### Docker ne démarre pas
```bash
open -a Docker  # macOS
```

### Port 8000 déjà utilisé
```bash
lsof -ti:8000 | xargs kill -9
```

## 📖 Documentation complète

Pour plus de détails, voir [README.old.md](README.old.md)

## 🤝 Contribution

Les contributions sont bienvenues ! Ouvrez une issue ou soumettez une Pull Request.

## 📄 License

MIT License

---

**Développé avec ❤️ en utilisant Claude Code**
