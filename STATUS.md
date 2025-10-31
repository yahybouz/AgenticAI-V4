# AgenticAI V4 - État Actuel

**Date:** 31 octobre 2025
**Version:** 4.0.0
**Statut:** ✅ Opérationnel en mode développement

---

## 🟢 Services Actifs

### Backend - http://localhost:8000
- **Status:** ✅ Running
- **API Framework:** FastAPI + Uvicorn
- **Database:** SQLite (mode développement)
- **Authentification:** JWT (HS256, 7 jours)
- **Agents:** 19 agents disponibles dans 8 domaines
- **Documentation API:** http://localhost:8000/docs

### Frontend - http://localhost:3001
- **Status:** ✅ Running
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite 5.4.21
- **Styling:** Tailwind CSS 3.4
- **State Management:** Zustand
- **Router:** React Router v6

---

## 🔐 Connexion Par Défaut

```
Email:    admin@agenticai.dev
Password: admin123
```

---

## ✅ Fonctionnalités Disponibles

### 1. Authentification & Gestion Utilisateurs
- ✅ Login / Logout
- ✅ Enregistrement de nouveaux utilisateurs
- ✅ Gestion de profil utilisateur
- ✅ Génération de clés API
- ✅ Statistiques utilisateur

### 2. Gestion des Agents
- ✅ Liste des agents disponibles (19 agents)
- ✅ Création d'agents personnalisés
- ✅ Configuration des domaines et compétences
- ✅ Gestion des modèles LLM (Ollama)

### 3. Orchestration Multi-Agents
- ✅ Orchestrateur maître
- ✅ Routage intelligent des requêtes
- ✅ Collaboration entre agents
- ✅ Gestion du contexte conversationnel

### 4. Chat & Conversations
- ✅ Interface de chat en temps réel
- ✅ Historique des conversations
- ✅ Streaming des réponses (SSE)
- ✅ Support multi-tours

### 5. Monitoring & Métriques
- ✅ Métriques système (CPU, RAM, disque)
- ✅ Métriques par agent (utilisation, latence)
- ✅ Health checks
- ✅ Logs structurés

---

## ⏸️ Fonctionnalités Désactivées (Docker requis)

Les fonctionnalités suivantes nécessitent `docker compose up -d` :

### PostgreSQL
- ⏸️ Base de données relationnelle production
- ⏸️ Scalabilité et résilience
- ⏸️ Migrations Alembic

### Qdrant (Vector Store)
- ⏸️ Recherche sémantique de documents
- ⏸️ Système RAG (Retrieval Augmented Generation)
- ⏸️ Upload de documents (PDF, DOCX, TXT, MD, JSON, CSV)
- ⏸️ Embeddings avec nomic-embed-text

### Redis
- ⏸️ Cache distribué
- ⏸️ Gestion des sessions
- ⏸️ File d'attente de tâches

---

## 📊 Architecture Actuelle

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│              http://localhost:3001                      │
│  Pages: Login, Register, Dashboard, Agents, Docs, Chat │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST + WebSocket
                     │
┌────────────────────▼────────────────────────────────────┐
│                   BACKEND (FastAPI)                     │
│              http://localhost:8000                      │
│  Routes: /api/auth, /api/agents, /api/orchestrator     │
│          /api/documents, /api/rag, /api/monitoring     │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌────────┐  ┌─────────┐
   │SQLite  │  │Ollama  │  │  19     │
   │(actif) │  │(dispo) │  │ Agents  │
   └────────┘  └────────┘  └─────────┘
```

---

## 🚀 Démarrage Rapide

### Mode Simple (Actuel)
```bash
# Backend
cd backend
PYTHONPATH="/Users/yahybouz/Desktop/Mes Scripts/AgenticAI-V4/backend" \
  backend/.venv/bin/python backend/api/main.py

# Frontend
cd frontend
npm run dev
```

### Mode Complet (avec Docker)
```bash
# Démarrer Docker Desktop, puis :
docker compose up -d
./run.sh
```

---

## 🧪 Tests

### Script de Test Complet
```bash
./scripts/test_all_features.sh
```

**Tests disponibles :**
1. ✅ Endpoints basiques (/, /health, /info, /docs)
2. ✅ Authentification (login, register, /api/auth/me)
3. ✅ Gestion utilisateurs (stats, profile)
4. ✅ Agents (list, available, create)
5. ✅ Orchestrateur (info, orchestrate)
6. ⏸️ Documents & RAG (nécessite Qdrant)
7. ✅ Monitoring (metrics, agents)
8. ✅ Frontend (accessibilité)

---

## 📈 Modèles LLM Disponibles (Ollama)

```bash
$ ollama list
qwen2.5:14b              # Principal (recommandé)
deepseek-r1:8b           # Raisonnement
llama3.1:latest          # Chat général
nomic-embed-text:latest  # Embeddings
phi3:mini                # Léger
qwen3:8b                 # Alternative
```

**Modèle actif par défaut:** `qwen2.5:14b`

---

## 🔧 Configuration

### Variables d'Environnement
```bash
# Backend
DATABASE_URL="sqlite+aiosqlite:///./agenticai.db"
JWT_SECRET_KEY="votre-clé-secrète"
OLLAMA_BASE_URL="http://localhost:11434"

# Frontend
VITE_API_URL="http://localhost:8000"
```

### Fichiers de Configuration
- `backend/config/settings.py` - Configuration backend
- `frontend/vite.config.ts` - Configuration Vite
- `docker-compose.yml` - Services Docker

---

## 📝 Prochaines Étapes

### À Faire Maintenant
- [ ] Tester l'interface frontend sur http://localhost:3001
- [ ] Créer un agent personnalisé
- [ ] Tester une conversation avec l'orchestrateur
- [ ] Vérifier les métriques de monitoring

### Pour Activer Toutes les Fonctionnalités
1. Démarrer Docker Desktop
2. Lancer `docker compose up -d`
3. Redémarrer le backend avec PostgreSQL
4. Tester l'upload de documents et la recherche RAG

---

## 🐛 Problèmes Connus

1. **Route /api/agents sans auth**
   - Symptôme: Retourne vide au lieu de 401
   - Impact: Mineur (fonctionnalité OK avec auth)
   - Statut: À investiguer

2. **Docker Credentials Warning**
   - Symptôme: `docker-credential-desktop not found`
   - Solution: Fichier `~/.docker/config.json` créé
   - Statut: ✅ Résolu

3. **Frontend Port 3000 Occupé**
   - Symptôme: Vite démarre sur port 3001
   - Solution: Utiliser http://localhost:3001
   - Statut: ✅ Comportement normal

---

## 📚 Documentation

- **Backend API:** http://localhost:8000/docs
- **Frontend:** Interface intuitive avec sidebar
- **Tests:** `./scripts/test_all_features.sh`
- **Setup:** `QUICKSTART.md`
- **Architecture:** `README.md`

---

## 📞 Support

Pour toute question ou problème :
1. Consulter les logs backend (terminal)
2. Consulter la console frontend (DevTools)
3. Vérifier `./scripts/test_all_features.sh`
4. Consulter la documentation API

---

**Dernière mise à jour:** 31 octobre 2025, 14:00
