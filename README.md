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

### 🔐 Authentification Multi-Utilisateurs
- **JWT Authentication** - Tokens sécurisés avec expiration (7 jours)
- **Rôles utilisateur** - Admin, User, Guest
- **Clés API** - Génération et validation sécurisée
- **Isolation des données** - Chaque utilisateur a son propre espace
- **Quotas personnalisés** - Limites d'agents, documents, stockage
- **Admin par défaut** - `admin@agenticai.dev` / `admin123`

### Système multi-agents
- **Orchestrateur intelligent** - Coordination automatique
- **Coach personnel** - Habitudes, objectifs, motivation
- **Email** - Rédaction, analyse de sentiment
- **Voice** - Transcription, synthèse vocale
- **Project Manager** - Planification, suivi
- **Web Intelligence** - Recherche, analyse
- **Documentation** - Génération, analyse
- **Agents personnalisés** - Création par utilisateur avec quotas

### RAG enrichi
- **Multi-formats** - PDF, DOCX, TXT, Markdown, HTML
- **Recherche sémantique** - Embedding via nomic-embed-text
- **Cache LRU** - Optimisation des performances
- **Reranking LLM** - Meilleure pertinence
- **Isolation par utilisateur** - Documents privés par défaut

## 🔧 Utilisation

### API Documentation
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Authentification

**Inscription :**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

**Connexion :**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
# Retourne: {"access_token": "eyJ...", "token_type": "bearer"}
```

**Utiliser le token :**
```bash
# Stocker le token
TOKEN="votre_token_jwt"

# Récupérer vos informations
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Upload de documents

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf" \
  -F "collection_name=documents"
```

### Recherche sémantique

```bash
curl -X POST "http://localhost:8000/api/documents/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Comment fonctionne le RAG ?",
    "top_k": 5,
    "enable_reranking": true
  }'
```

### Créer un agent personnalisé

```bash
curl -X POST "http://localhost:8000/api/agents/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mon Agent",
    "domain": "RAG",
    "skills": ["search", "analyze"],
    "description": "Agent personnalisé",
    "input_schema": {},
    "output_schema": {}
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

# Tester le système d'authentification (in-memory)
python scripts/test_auth.py

# Tester le système d'authentification avec PostgreSQL
python scripts/test_postgres_auth.py

# Tester le système RAG
python scripts/test_enhanced_rag.py

# Tester les routes protégées (nécessite l'API en cours d'exécution)
./scripts/test_protected_routes.sh
```

## 🗄️ Migrations de base de données

Le système utilise Alembic pour gérer les migrations PostgreSQL.

### Voir les migrations disponibles
```bash
cd backend
alembic history
```

### Appliquer les migrations
```bash
cd backend
alembic upgrade head
```

### Créer une nouvelle migration (après modification des modèles)
```bash
cd backend
# Auto-générer depuis les modèles SQLAlchemy
alembic revision --autogenerate -m "Description de la migration"

# Ou créer manuellement
alembic revision -m "Description de la migration"
```

### Revenir en arrière
```bash
cd backend
# Revenir à la migration précédente
alembic downgrade -1

# Revenir au début
alembic downgrade base
```

### État actuel
```bash
cd backend
alembic current
```

**Note :** Les migrations sont automatiquement appliquées au démarrage de l'application via `user_service.init_db()`.

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
