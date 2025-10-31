# 🚀 Guide de Démarrage Rapide - AgenticAI V4

## Option 1: Test rapide (Sans Docker) ⚡

Pour tester l'interface rapidement sans installer Docker/PostgreSQL/Ollama :

```bash
./quick-start.sh
```

Puis ouvrir http://localhost:3000

**Login par défaut:**
- Email: `admin@agenticai.dev`
- Password: `admin123`

**Note:** Mode développement avec SQLite (données en mémoire, pas de persistence)

---

## Option 2: Installation Complète (Recommandé) 🏗️

Pour une installation complète avec toutes les fonctionnalités :

### 1. Installation

```bash
./setup.sh
```

Ce script installe automatiquement :
- Docker Desktop
- Ollama + modèles LLM
- PostgreSQL, Qdrant, Redis
- Toutes les dépendances Python et Node.js

### 2. Démarrage

```bash
./run.sh
```

Services lancés :
- 🌐 Frontend React: http://localhost:3000
- 🔧 API Backend: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 🔍 Qdrant Dashboard: http://localhost:6333/dashboard
- 🤖 Ollama: http://localhost:11434

### 3. Arrêt

```bash
./stop.sh
# OU
Ctrl+C dans le terminal
```

---

## Fonctionnalités Disponibles

### Interface Web (localhost:3000)

#### 📊 Dashboard
- Statistiques utilisateur en temps réel
- Quotas (agents, documents, stockage)
- Vue système globale

#### 🤖 Agents
- Liste des agents disponibles (système + personnalisés)
- Création d'agents personnalisés
- Suppression d'agents
- Affichage des compétences

#### 📄 Documents
- Upload de documents (PDF, DOCX, TXT, MD, HTML)
- Recherche sémantique avec reranking
- Liste des documents uploadés
- Suppression de documents

#### 💬 Chat
- Interface de conversation avec les agents
- Messages en temps réel
- Historique des conversations

---

## API REST (localhost:8000)

### Authentification

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@agenticai.dev",
    "password": "admin123"
  }'
```

**Get Profile:**
```bash
TOKEN="your_jwt_token"

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Agents

**Create Agent:**
```bash
curl -X POST http://localhost:8000/api/agents/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mon Agent",
    "domain": "RAG",
    "skills": ["search", "analyze"],
    "description": "Agent personnalisé"
  }'
```

**List Agents:**
```bash
curl -X GET http://localhost:8000/api/agents/ \
  -H "Authorization: Bearer $TOKEN"
```

### Documents

**Upload Document:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf" \
  -F "collection_name=documents"
```

**Search Documents:**
```bash
curl -X POST http://localhost:8000/api/documents/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Comment fonctionne le RAG ?",
    "top_k": 5,
    "enable_reranking": true
  }'
```

---

## Configuration

### Base de données

**Développement (SQLite - défaut):**
```
postgres_url = "sqlite+aiosqlite:///./agenticai.db"
```

**Production (PostgreSQL):**
```
postgres_url = "postgresql+asyncpg://agenticai:agenticai@localhost:5432/agenticai"
```

Modifier dans `backend/config/settings.py`

### Frontend

Variables d'environnement dans `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

---

## Troubleshooting

### Port 8000 déjà utilisé
```bash
lsof -ti:8000 | xargs kill -9
```

### Port 3000 déjà utilisé
```bash
lsof -ti:3000 | xargs kill -9
```

### Docker ne démarre pas
```bash
# macOS
open /Applications/Docker.app

# Ou depuis Finder > Applications > Docker
```

### Backend ne démarre pas

Vérifier les logs:
```bash
tail -f /tmp/backend.log
```

Relancer manuellement:
```bash
cd backend
PYTHONPATH="$(pwd)" .venv/bin/uvicorn api.main:app --reload
```

### Frontend ne démarre pas

Réinstaller les dépendances:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## Architecture

```
AgenticAI-V4/
├── frontend/          # React 18 + TypeScript + Vite
│   ├── src/
│   │   ├── pages/     # Dashboard, Agents, Documents, Chat
│   │   ├── components/# Layout, UI components
│   │   ├── services/  # API client
│   │   ├── store/     # Zustand state
│   │   └── types/     # TypeScript definitions
│   └── package.json
│
├── backend/           # FastAPI + Python 3.11+
│   ├── api/          # Routes & endpoints
│   ├── agents/       # Agent implementations
│   ├── services/     # Business logic
│   ├── models/       # Pydantic & SQLAlchemy
│   └── alembic/      # DB migrations
│
├── scripts/          # Utility scripts
├── setup.sh          # Installation
├── run.sh            # Launch (full)
├── quick-start.sh    # Launch (no Docker)
└── stop.sh           # Shutdown
```

---

## Support

- Documentation: `/docs`
- API Documentation: http://localhost:8000/docs
- GitHub Issues: https://github.com/yahybouz/AgenticAI-V4/issues

---

**Développé avec ❤️ et Claude Code**
