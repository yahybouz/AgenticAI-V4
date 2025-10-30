# AgenticAI V4 - Assistant Multi-Agents Local

**Version:** 4.0.0
**Date:** Janvier 2025
**Architecture:** Multi-agents orchestrés, 100% local via Ollama

---

## 🎯 Vision

Assistant IA agentique complet avec orchestration adaptative, 100% local (modèles via Ollama), extensible et modulaire.

### Fonctionnalités Principales

- 🎤 **Voix Temps Réel:** Transcription → Traduction → Q&A live
- 📧 **E-mail Intelligent:** Lecture, classification, synthèse, rédaction
- 🧠 **Chat RAG:** Mémoire longue, création d'agents par langage naturel
- 💪 **Coach Santé:** Suivi via WhatsApp, rapports multi-granularité
- 📄 **Rédaction Académique:** Mémoires, rapports, avec relecture anti-hallucination
- 🔍 **Recherche Web:** Agents de veille et fact-checking
- 📝 **Comptes Rendus:** Templates personnalisables, export multi-formats

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                    │
│  Dashboard │ Voix Live │ E-mail │ Chat │ Coach │ CR    │
└────────────────────────┬────────────────────────────────┘
                         │ WebSocket + REST
┌────────────────────────▼────────────────────────────────┐
│              Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────┐      │
│  │       Master Orchestrator                    │      │
│  │  Politiques │ Quotas │ Arbitrage │ Validation│      │
│  └──────────┬───────────────────────────────────┘      │
│             │                                            │
│  ┌──────────▼─────┬──────────┬──────────┬────────┐    │
│  │ Sub-Orch       │ Sub-Orch │ Sub-Orch │ Sub-   │    │
│  │ Voice          │ Mail     │ RAG      │ Coach  │    │
│  └──┬─────────────┴────┬─────┴────┬─────┴────┬───┘    │
│     │                  │          │          │         │
│  ┌──▼──────┐  ┌───────▼───┐  ┌───▼────┐  ┌──▼──┐    │
│  │ Agents  │  │  Agents   │  │ Agents │  │Agents│   │
│  │ Voice.* │  │  Mail.*   │  │ RAG.*  │  │Coach*│   │
│  └─────────┘  └───────────┘  └────────┘  └──────┘    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  Services Locaux                        │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐ │
│  │ Ollama  │  │ Postgres │  │ Qdrant │  │  Redis   │ │
│  │ LLM +   │  │   SQL    │  │Vectors │  │Event Bus │ │
│  │Embeddings│  │          │  │        │  │          │ │
│  └─────────┘  └──────────┘  └────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Stack Technique

### Backend
- **Framework:** FastAPI (async natif)
- **Orchestration:** Master + sous-orchestrateurs par domaine
- **Workers (à venir):** Celery + Redis
- **Base de données:** PostgreSQL (états, configs)
- **Vector DB:** Qdrant (embeddings)
- **Event Bus:** Redis Streams
- **Storage:** MinIO (fichiers audio, docs)

### Frontend
- **Framework:** Next.js 14 + React 18
- **UI:** Tailwind CSS + shadcn/ui
- **État:** Zustand
- **Temps réel:** WebSocket

### IA (100% Local via Ollama)
- **LLM Principal:** `qwen2.5:14b` (multilingue, raisonnement)
- **LLM Rapide:** `phi4:latest` (tâches simples)
- **Code:** `qwen2.5-coder:7b`
- **Embeddings:** `nomic-embed-text:latest` (long context)
- **Multimodal:** `llava:13b` (vision)
- **ASR:** `whisper:large-v3` (transcription)

### Intégrations
- **E-mail:** OAuth2 Gmail/Outlook
- **WhatsApp:** Business API (webhook)
- **Web Search:** SearxNG local

---

## ⚙️ Prérequis

- **Python 3.11+**
- **Ollama** installé localement avec les modèles requis (`ollama pull ...`)
- **Docker / Docker Compose** (recommandé pour Postgres, Qdrant, Redis, MinIO)
- **Node.js 20+** (pour le frontend Next.js)

---

## 🧪 Démarrer le backend

1. **Installer les dépendances Python**
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```

2. **Configurer l’environnement**
   ```bash
   cp ../.env.example ../.env
   # ajuster les URLs (Postgres, Qdrant, Redis, MinIO, Ollama…)
   ```

3. **Lancer les services de base** (Docker recommandé, ex. Postgres/Qdrant/Redis/MinIO)

4. **Démarrer l’API FastAPI**
   ```bash
   cd ..
   ./scripts/run-backend.sh
   ```

5. **Tester**
   ```bash
   cd backend
   pytest
   ```

L’API est disponible sur `http://localhost:8000` (docs Swagger sur `/docs`).

---

## 🔌 API Backend (extraits)

| Domaine     | Endpoint                                | Description                                |
|-------------|------------------------------------------|--------------------------------------------|
| Voice       | `POST /api/voice/session`                | Démarre une session voix (orchestration)   |
| Voice       | `POST /api/voice/bookmark`               | Enregistre un marqueur Action/Décision     |
| Mail        | `POST /api/mail/summarize`               | Synthèse d’un thread mail                   |
| Mail        | `POST /api/mail/reply`                   | Brouillon de réponse HITL                   |
| Mail        | `POST /api/mail/send`                    | Demande d’envoi (garde-fou)                 |
| RAG         | `POST /api/rag/search`                   | Recherche hybride (stub/vectorstore)        |
| Coach       | `POST /api/coach/log`                    | Ajout d’un log santé                        |
| Docs        | `POST /api/docs/cr/build`                | Génération de compte-rendu                  |
| WebIntel    | `POST /api/webintel/query`               | Brief sourcé (crawler + fact-check)         |
| PM          | `POST /api/pm/risks/analyze`             | Analyse des risques projet                  |
| Agents      | `GET/POST/DELETE /api/agents`            | Registry d’agents                           |
| Monitoring  | `GET /api/monitoring/insights`           | Insights de qualité                         |
| Orchestrator| `POST /api/orchestrator/policy`          | Mise à jour des politiques                  |

> Les orchestrateurs appellent des services stub (Ollama, Postgres, Qdrant, Redis) avec fallback mémoire pour fonctionner même sans stack complète.

---

## 🖥️ Frontend (Next.js 14 – TODO)

- Structure à venir : `frontend/app`, `frontend/components`, `frontend/lib`
- Design cible :
  - Dashboard multi-domaines (Réunions, E-mails, Santé, Docs, WebIntel, PM)
  - Live meeting widget (sous-titres, traduction, marqueurs)
  - Chat latéral (RAG + commandes agentiques)
  - Boîte d’envoi pour workflows HITL

👉 Un scaffold Next.js + Tailwind sera ajouté pour consommer l’API (`/api/*`) et les WebSockets (`/ws/chat`, `/ws/voice`).

---

## 📦 Structure Projet

```
AgenticAI-V4/
├── backend/
│   ├── api/              # Routes FastAPI
│   ├── orchestrators/    # Master + Sub-orchestrators
│   ├── agents/           # Registry d’agents
│   ├── api/              # Routes FastAPI
│   ├── orchestrators/    # Master + sous-orchestrateurs
│   ├── services/         # Connecteurs Ollama/DB/Qdrant/Redis
│   ├── models/           # Data models Pydantic
│   ├── tests/            # Tests Pytest
│   └── config/           # Settings Pydantic
├── frontend/
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   └── lib/              # Utils, API client
├── docker/
│   ├── docker-compose.yml
│   └── services/         # Dockerfiles
├── config/
│   ├── agents/           # Agent registry (YAML)
│   ├── orchestrators/    # Policies (YAML)
│   └── templates/        # CR templates
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── agents.md
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 🎯 Agents Disponibles

### Domaine Voice (Voix)
- `Voice.Capture` - Capture audio micro/loopback
- `Voice.Transcribe` - ASR whisper local
- `Voice.Translate` - Traduction LLM
- `Voice.QA` - Q&A sur transcript live

### Domaine Mail (E-mail)
- `Mail.Ingest` - Connexion Gmail/Outlook OAuth
- `Mail.Classify` - Classification priorité/thème
- `Mail.Summarize` - Résumé threads
- `Mail.ReplyDraft` - Rédaction réponses
- `Mail.Send` - Envoi avec HITL

### Domaine RAG (Recherche)
- `RAG.Indexer` - Chunking + embeddings
- `RAG.Searcher` - Recherche hybride (BM25 + vecteurs)
- `RAG.Citation` - Extraction sources

### Domaine Coach (Santé)
- `Coach.LogIngest` - Parsing WhatsApp
- `Coach.Analyst` - Calculs bilan/tendances
- `Coach.Reporter` - Rapports quotidien/hebdo/mensuel
- `Coach.Alerter` - Notifications seuils

### Domaine Writer (Rédaction)
- `Writer.Academic` - Mémoires, rapports, thèses
- `Writer.CR` - Comptes rendus réunion
- `Writer.Email` - E-mails professionnels

### Domaine Reviewer (Relecture)
- `Reviewer.Hallucination` - Détection incohérences
- `Reviewer.Citation` - Vérification références
- `Reviewer.Style` - Conformité académique
- `Reviewer.Fact` - Fact-checking

### Domaine Web (Internet)
- `Web.Search` - Recherche multi-moteurs
- `Web.Scraper` - Extraction contenu propre
- `Web.FactChecker` - Vérification multi-sources
- `Web.Monitor` - Veille automatique

---

## 📋 Roadmap

### Phase 1: Infrastructure (Semaines 1-2) ✅ EN COURS
- [x] Structure projet
- [ ] Docker Compose complet
- [ ] Base PostgreSQL + migrations
- [ ] Qdrant + premier index
- [ ] Orchestrateur Master basique
- [ ] API FastAPI minimale
- [ ] Frontend Next.js skeleton

### Phase 2: Chat RAG (Semaines 2-3)
- [ ] RAG.Indexer (chunking + embeddings)
- [ ] RAG.Searcher (recherche hybride)
- [ ] Chat avec mémoire longue
- [ ] UI chat + citations
- [ ] Tests latence/pertinence

### Phase 3: Voix Live (Semaines 3-5)
- [ ] Voice.Capture (audio streaming)
- [ ] Voice.Transcribe (whisper local)
- [ ] Voice.Translate (LLM)
- [ ] Voice.QA (RAG live)
- [ ] Widget overlay réunion
- [ ] Export transcripts

### Phase 4: E-mail (Semaines 5-7)
- [ ] Mail.Ingest (OAuth Gmail/Outlook)
- [ ] Mail.Classify (ML classification)
- [ ] Mail.Summarize (résumés)
- [ ] Mail.ReplyDraft (rédaction)
- [ ] Workflow HITL
- [ ] Tests précision

### Phase 5: Coach Santé (Semaines 7-8)
- [ ] Bot WhatsApp (webhook)
- [ ] Coach.LogIngest (parsing)
- [ ] Coach.Analyst (calculs)
- [ ] Rapports multi-granularité
- [ ] Alertes paramétrables

### Phase 6: Rédaction Académique (Semaines 8-10)
- [ ] Writer.Academic (templates)
- [ ] Reviewer.Hallucination (détection)
- [ ] Reviewer.Citation (vérif)
- [ ] Boucle itérative Writer→Reviewer
- [ ] Export multi-formats

### Phase 7: Recherche Web (Semaines 10-11)
- [ ] Web.Search (multi-moteurs)
- [ ] Web.Scraper (extraction)
- [ ] Web.FactChecker (vérification)
- [ ] Indexation automatique RAG

### Phase 8: Agents Dynamiques (Semaines 11-12)
- [ ] Création agents via langage naturel
- [ ] Validation specs + coûts
- [ ] Registry dynamique
- [ ] Garde-fous actifs

---

## ⚙️ Configuration

Voir `config/README.md` pour détails complets.

### Modèles Ollama à Télécharger

```bash
# LLM
ollama pull qwen2.5:14b
ollama pull phi4:latest
ollama pull qwen2.5-coder:7b

# Embeddings
ollama pull nomic-embed-text:latest

# Multimodal
ollama pull llava:13b

# ASR (si disponible via Ollama)
ollama pull whisper:large-v3
```

### Variables d'Environnement

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Base de données
POSTGRES_URL=postgresql://user:pass@localhost:5432/agenticai
QDRANT_URL=http://localhost:6333
REDIS_URL=redis://localhost:6379

# E-mail OAuth
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
OUTLOOK_CLIENT_ID=...
OUTLOOK_CLIENT_SECRET=...

# WhatsApp
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_WEBHOOK_VERIFY_TOKEN=...

# Sécurité
SECRET_KEY=...
JWT_SECRET=...
```

---

## 🚀 Démarrage Rapide

```bash
# 1. Cloner et installer
git clone <repo>
cd AgenticAI-V4

# 2. Démarrer les services
docker compose up -d

# 3. Télécharger les modèles Ollama
./scripts/download-models.sh

# 4. Migrations DB
cd backend
alembic upgrade head

# 5. Seed data (agents registry, policies)
python scripts/seed.py

# 6. Démarrer backend
uvicorn api.main:app --reload --port 8000

# 7. Démarrer frontend
cd ../frontend
npm install
npm run dev

# 8. Accéder
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - Docs API: http://localhost:8000/docs
# - Qdrant: http://localhost:6333/dashboard
```

---

## 🧪 Tests

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# E2E tests
pytest tests/e2e

# Performance (latence, WER)
pytest tests/performance

# Sécurité
pytest tests/security
```

---

## 📊 Monitoring

- **Logs:** Structured JSON (stdout)
- **Traces:** OpenTelemetry → Jaeger
- **Métriques:** Prometheus → Grafana
- **Dashboards:** Latence, WER, TPM, coûts

Accès: http://localhost:3001 (Grafana)

---

## 🔐 Sécurité

- ✅ Données 100% local (sauf APIs externes)
- ✅ Chiffrement au repos (Postgres, fichiers)
- ✅ TLS en transit
- ✅ RBAC (Admin, Power User, User)
- ✅ Audit trail (toutes actions agents)
- ✅ Secrets en vault local
- ✅ OAuth scopes minimaux
- ✅ Panic switch (gel création agents)

---

## 📚 Documentation

- [Architecture détaillée](docs/architecture.md)
- [API Reference](docs/api.md)
- [Guide Agents](docs/agents.md)
- [Orchestration](docs/orchestration.md)
- [Templates CR](docs/templates.md)
- [Déploiement](docs/deployment.md)

---

## 🤝 Contribution

Voir [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

---

## 🆘 Support

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Docs: [docs/](docs/)

---

**Version:** 4.0.0
**Status:** 🚧 En développement actif
**Dernière mise à jour:** Janvier 2025
