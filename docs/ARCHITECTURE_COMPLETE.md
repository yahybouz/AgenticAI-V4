# Architecture Technique Complète - AgenticAI V4

**Version:** 4.0.0
**Date:** 26 Janvier 2025

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture en Couches](#architecture-en-couches)
3. [Schémas Techniques](#schémas-techniques)
4. [Flux de Données](#flux-de-données)
5. [Stack Technique](#stack-technique)
6. [Base de Données](#base-de-données)
7. [Orchestration](#orchestration)
8. [Agents](#agents)
9. [Sécurité](#sécurité)
10. [Déploiement](#déploiement)

---

## 1. Vue d'Ensemble

### Principe Fondamental

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│   Utilisateur interagit via UI (Web/Mobile/Voice/WhatsApp)  │
│                                                               │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                         │
│  ┌──────────────────────────────────────────────────┐       │
│  │          MASTER ORCHESTRATOR                     │       │
│  │  • Politiques globales                           │       │
│  │  • Arbitrage ressources                          │       │
│  │  • Quotas & garde-fous                           │       │
│  │  • Validation création agents                     │       │
│  └───────────┬──────────────────────────────────────┘       │
│              │                                                │
│   ┌──────────┴───────────┬──────────────┬──────────────┐   │
│   │                      │              │              │   │
│   ▼                      ▼              ▼              ▼   │
│  Voice                  Mail           RAG           Coach  │
│  Sub-Orch            Sub-Orch       Sub-Orch      Sub-Orch │
└───┬──────────────────────┬──────────────┬──────────────┬───┘
    │                      │              │              │
    ▼                      ▼              ▼              ▼
┌───────────────────────────────────────────────────────────┐
│                    AGENTS LAYER                            │
│  Voice.Capture      Mail.Ingest      RAG.Indexer         │
│  Voice.Transcribe   Mail.Classify    RAG.Searcher        │
│  Voice.Translate    Mail.Summarize   RAG.Citation        │
│  Voice.QA           Mail.Reply       Writer.Academic     │
│                     Web.Search       Reviewer.*          │
└───┬──────────────────────┬──────────────┬───────────────┘
    │                      │              │
    ▼                      ▼              ▼
┌───────────────────────────────────────────────────────────┐
│                   SERVICES LAYER                           │
│  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐    │
│  │ Ollama  │  │ Postgres │  │ Qdrant │  │  Redis   │    │
│  │ (LLM)   │  │  (SQL)   │  │(Vector)│  │  (Bus)   │    │
│  └─────────┘  └──────────┘  └────────┘  └──────────┘    │
└───────────────────────────────────────────────────────────┘
```

### Caractéristiques Clés

✅ **100% Local** - Tous les modèles IA via Ollama
✅ **Modulaire** - Ajout features sans casser existant
✅ **Scalable** - Orchestration adaptative
✅ **Observable** - Logs, traces, métriques
✅ **Sécurisé** - RBAC, audit trail, chiffrement

---

## 2. Architecture en Couches

### 2.1 Couche Présentation (Layer 1)

```
┌────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                         │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Web App    │  │   WhatsApp   │  │    Voice     │    │
│  │  (Next.js)   │  │     Bot      │  │   Widget     │    │
│  │              │  │              │  │   (Overlay)  │    │
│  │ • Dashboard  │  │ • Webhook    │  │ • Subtitles  │    │
│  │ • Chat       │  │ • Commands   │  │ • Controls   │    │
│  │ • Settings   │  │ • Logs       │  │ • Markers    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                                │
│                            ▼                                │
│                   ┌─────────────────┐                      │
│                   │   API Gateway   │                      │
│                   │   (FastAPI)     │                      │
│                   └─────────────────┘                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘

Protocoles:
- HTTP/REST (API classique)
- WebSocket (temps réel: chat, voix)
- Webhook (WhatsApp, intégrations externes)
```

### 2.2 Couche Orchestration (Layer 2)

```
┌──────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                          │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │          MASTER ORCHESTRATOR                           │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │                                                          │  │
│  │  Responsabilités:                                       │  │
│  │  • Load Policies (YAML)                                │  │
│  │  • Validate Agent Creation Requests                    │  │
│  │  • Arbitrate Resource Conflicts                        │  │
│  │  • Enforce Quotas & Rate Limits                        │  │
│  │  • Monitor System Health                               │  │
│  │  • Emergency Panic Switch                              │  │
│  │                                                          │  │
│  │  Policies:                                              │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │ max_concurrent_agents: 12                        │ │  │
│  │  │ creation_rate_limit_per_min: 3                   │ │  │
│  │  │ guarded_actions:                                 │ │  │
│  │  │   - send_email_external                          │ │  │
│  │  │   - delete_content                               │ │  │
│  │  │ require_human_approval:                          │ │  │
│  │  │   - send_email_external                          │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  └────────────────────┬───────────────────────────────────┘  │
│                       │                                        │
│    ┌──────────────────┼───────────────────────────────┐      │
│    │                  │                               │      │
│    ▼                  ▼                               ▼      │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Voice         │  │ Mail          │  │ RAG/Chat      │   │
│  │ Sub-Orch      │  │ Sub-Orch      │  │ Sub-Orch      │   │
│  ├───────────────┤  ├───────────────┤  ├───────────────┤   │
│  │ • Capture     │  │ • Ingest      │  │ • Index       │   │
│  │ • Transcribe  │  │ • Classify    │  │ • Search      │   │
│  │ • Translate   │  │ • Summarize   │  │ • Cite        │   │
│  │ • QA          │  │ • Reply       │  │ • Generate    │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Coach         │  │ Writer        │  │ Web           │   │
│  │ Sub-Orch      │  │ Sub-Orch      │  │ Sub-Orch      │   │
│  ├───────────────┤  ├───────────────┤  ├───────────────┤   │
│  │ • Log Ingest  │  │ • Academic    │  │ • Search      │   │
│  │ • Analyst     │  │ • CR          │  │ • Scrape      │   │
│  │ • Reporter    │  │ • Reviewer    │  │ • Fact-Check  │   │
│  │ • Alerter     │  │ • Citation    │  │ • Monitor     │   │
│  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                │
│  Communication:                                               │
│  • Event Bus (Redis Streams)                                 │
│  • Message Queue (Celery/Redis)                              │
│  • Shared State (Postgres)                                   │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 Couche Agents (Layer 3)

```
┌──────────────────────────────────────────────────────────────┐
│                     AGENTS LAYER                              │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Structure d'un Agent:                                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Agent: voice.transcribe                               │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Metadata:                                             │  │
│  │  • name: "Voice Transcribe"                            │  │
│  │  • domain: "voice"                                     │  │
│  │  • skills: [speech_to_text, multilingual]             │  │
│  │  • latency_ms: 2000                                    │  │
│  │  • cost: high                                          │  │
│  │                                                          │  │
│  │  Models:                                                │  │
│  │  • whisper:large-v3 (Ollama)                           │  │
│  │                                                          │  │
│  │  Config:                                                │  │
│  │  • language: auto                                       │  │
│  │  • task: transcribe                                     │  │
│  │  • beam_size: 5                                         │  │
│  │                                                          │  │
│  │  Lifecycle:                                             │  │
│  │  ┌──────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │  │
│  │  │ Created  │─>│ Running │─>│ Paused  │─>│ Stopped │ │  │
│  │  └──────────┘  └─────────┘  └─────────┘  └─────────┘ │  │
│  │                                                          │  │
│  │  Input/Output:                                          │  │
│  │  Input: audio_stream (bytes)                           │  │
│  │  Output: transcript_text (string + timestamps)         │  │
│  │                                                          │  │
│  │  Monitoring:                                            │  │
│  │  • Latency tracking                                     │  │
│  │  • Error rate                                           │  │
│  │  • Resource usage (GPU/CPU)                            │  │
│  │  • Audit trail (all actions logged)                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Agent Types (28 agents total):                              │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │ Voice (4)    │ Mail (5)     │ RAG (3)      │             │
│  │ Coach (4)    │ Writer (2)   │ Reviewer (3) │             │
│  │ Web (4)      │ Custom (3+)  │              │             │
│  └──────────────┴──────────────┴──────────────┘             │
│                                                                │
│  Registry:                                                    │
│  • Stored in config/agents/registry.yaml                     │
│  • Loaded at startup                                          │
│  • Dynamically extensible                                     │
│  • Versioned                                                  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### 2.4 Couche Services (Layer 4)

```
┌──────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER                             │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌───────────────────┐  ┌───────────────────┐               │
│  │     OLLAMA        │  │    POSTGRESQL     │               │
│  │  (AI Models)      │  │  (Structured DB)  │               │
│  ├───────────────────┤  ├───────────────────┤               │
│  │ LLM:              │  │ Tables:           │               │
│  │ • qwen2.5:14b     │  │ • agents          │               │
│  │ • phi4:latest     │  │ • orchestrators   │               │
│  │ • qwen2.5-coder   │  │ • events          │               │
│  │                   │  │ • documents       │               │
│  │ Embeddings:       │  │ • emails          │               │
│  │ • nomic-embed-text│  │ • health_logs     │               │
│  │                   │  │ • templates       │               │
│  │ ASR:              │  │ • users           │               │
│  │ • whisper:large-v3│  │ • policies        │               │
│  │                   │  │                   │               │
│  │ Multimodal:       │  │ Features:         │               │
│  │ • llava:13b       │  │ • ACID            │               │
│  │                   │  │ • Migrations      │               │
│  │ API: :11434       │  │ • Backups         │               │
│  └───────────────────┘  │ • Port: 5432      │               │
│                          └───────────────────┘               │
│                                                                │
│  ┌───────────────────┐  ┌───────────────────┐               │
│  │     QDRANT        │  │      REDIS        │               │
│  │  (Vector DB)      │  │  (Cache/Bus)      │               │
│  ├───────────────────┤  ├───────────────────┤               │
│  │ Collections:      │  │ Uses:             │               │
│  │ • agenticai_rag   │  │ • Cache           │               │
│  │ • voice_trans     │  │ • Event Bus       │               │
│  │ • mail_threads    │  │ • Celery Broker   │               │
│  │ • documents       │  │ • Session Store   │               │
│  │                   │  │ • Rate Limiting   │               │
│  │ Features:         │  │                   │               │
│  │ • Cosine distance │  │ Structures:       │               │
│  │ • Hybrid search   │  │ • Streams         │               │
│  │ • Filters         │  │ • Pub/Sub         │               │
│  │ • Dashboard       │  │ • Sorted Sets     │               │
│  │                   │  │                   │               │
│  │ API: :6333        │  │ Port: 6379        │               │
│  └───────────────────┘  └───────────────────┘               │
│                                                                │
│  ┌───────────────────┐  ┌───────────────────┐               │
│  │     MINIO         │  │     CELERY        │               │
│  │ (Object Storage)  │  │  (Task Queue)     │               │
│  ├───────────────────┤  ├───────────────────┤               │
│  │ Buckets:          │  │ Queues:           │               │
│  │ • audio-files     │  │ • voice.high      │               │
│  │ • transcripts     │  │ • mail.medium     │               │
│  │ • documents       │  │ • rag.low         │               │
│  │ • exports         │  │ • coach.scheduled │               │
│  │ • backups         │  │                   │               │
│  │                   │  │ Workers:          │               │
│  │ Features:         │  │ • 4 concurrent    │               │
│  │ • S3 compatible   │  │ • Auto-retry      │               │
│  │ • Versioning      │  │ • Priority        │               │
│  │ • Encryption      │  │                   │               │
│  │                   │  │ Beat:             │               │
│  │ API: :9000        │  │ • Scheduled tasks │               │
│  │ Console: :9001    │  │ • Cron-like       │               │
│  └───────────────────┘  └───────────────────┘               │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### 2.5 Couche Observabilité (Layer 5)

```
┌──────────────────────────────────────────────────────────────┐
│                 OBSERVABILITY LAYER                           │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌───────────────────┐  ┌───────────────────┐               │
│  │   JAEGER          │  │   PROMETHEUS      │               │
│  │ (Tracing)         │  │  (Metrics)        │               │
│  ├───────────────────┤  ├───────────────────┤               │
│  │ • Distributed     │  │ Metrics:          │               │
│  │   traces          │  │ • Latency         │               │
│  │ • Span analysis   │  │ • Throughput      │               │
│  │ • Dependency      │  │ • Error rate      │               │
│  │   graph           │  │ • Resource usage  │               │
│  │ • UI: :16686      │  │ • Custom counters │               │
│  └───────────────────┘  │ • API: :9090      │               │
│                          └───────────────────┘               │
│                                                                │
│  ┌───────────────────┐  ┌───────────────────┐               │
│  │   GRAFANA         │  │   LOGS            │               │
│  │  (Dashboards)     │  │ (Structured JSON) │               │
│  ├───────────────────┤  ├───────────────────┤               │
│  │ Dashboards:       │  │ Levels:           │               │
│  │ • System overview │  │ • DEBUG           │               │
│  │ • Agent metrics   │  │ • INFO            │               │
│  │ • Voice latency   │  │ • WARNING         │               │
│  │ • Mail throughput │  │ • ERROR           │               │
│  │ • RAG performance │  │ • CRITICAL        │               │
│  │                   │  │                   │               │
│  │ Alerts:           │  │ Fields:           │               │
│  │ • Email           │  │ • timestamp       │               │
│  │ • Webhook         │  │ • level           │               │
│  │ • Slack           │  │ • agent_id        │               │
│  │                   │  │ • action          │               │
│  │ UI: :3001         │  │ • duration_ms     │               │
│  └───────────────────┘  │ • error_message   │               │
│                          └───────────────────┘               │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Schémas Techniques

### 3.1 Flux Voix Temps Réel

```
┌──────────────────────────────────────────────────────────────┐
│              FLUX VOIX TEMPS RÉEL                             │
└──────────────────────────────────────────────────────────────┘

Utilisateur parle
      │
      ▼
┌─────────────┐
│   Micro     │  Audio brut (PCM 16kHz mono)
│  (Browser)  │
└──────┬──────┘
       │ WebSocket
       │ Chunks 100ms
       ▼
┌────────────────────────┐
│ Voice.Capture Agent    │  VAD + Buffer
│ (Backend)              │  Packets 1-2s
└──────┬─────────────────┘
       │
       │ Audio packets
       ▼
┌────────────────────────┐
│ Voice.Transcribe Agent │  whisper:large-v3
│ (Ollama)               │  Latency: ~2s
└──────┬─────────────────┘
       │
       │ Text + Timestamps
       ▼
    ┌──┴───┐
    │      │
    ▼      ▼
┌────────┐ ┌──────────────────┐
│Display │ │Voice.Translate   │  qwen2.5:14b
│Subtitles│ │Agent (Ollama)    │  Latency: ~1s
└────────┘ └──────┬───────────┘
                  │
                  │ Translated text
                  ▼
           ┌──────────────┐
           │ Display      │
           │ Translation  │
           └──────┬───────┘
                  │
                  ▼
           ┌──────────────────┐
           │ RAG.Indexer      │  nomic-embed-text
           │ (Background)     │  Chunking + Embeddings
           └──────┬───────────┘
                  │
                  │ Vectors
                  ▼
           ┌──────────────┐
           │   Qdrant     │  Indexed for Q&A
           └──────────────┘
                  │
                  │ Query
                  ▼
           ┌──────────────────┐
           │ Voice.QA Agent   │  RAG + qwen2.5:14b
           │                  │  Latency: ~2s
           └──────┬───────────┘
                  │
                  │ Answer + Citations
                  ▼
           ┌──────────────┐
           │    Display   │
           │    Answer    │
           └──────────────┘

Total latency (parole → sous-titre): 3-4s
Total latency (parole → traduction): 4-5s
Total latency (question → réponse): 2-3s
```

### 3.2 Flux E-mail

```
┌──────────────────────────────────────────────────────────────┐
│                    FLUX E-MAIL                                │
└──────────────────────────────────────────────────────────────┘

┌──────────────┐
│ Gmail/Outlook│  OAuth2 Connection
│   Account    │
└──────┬───────┘
       │
       │ API Call (every 5 min)
       ▼
┌────────────────────────┐
│ Mail.Ingest Agent      │  Fetch threads + metadata
│                        │  Batch: 50 emails
└──────┬─────────────────┘
       │
       │ Email threads
       ▼
┌────────────────────────┐
│ Mail.Classify Agent    │  phi4:latest
│                        │  Priority + Theme + Sentiment
│                        │  Latency: ~500ms/email
└──────┬─────────────────┘
       │
       │ Classified threads
       ▼
┌────────────────────────┐
│   Postgres DB          │  Store metadata + labels
│   (emails table)       │
└──────┬─────────────────┘
       │
       │ User request: "Summarize finance emails"
       ▼
┌────────────────────────┐
│ Mail.Summarize Agent   │  qwen2.5:14b
│                        │  • Bullets
│                        │  • Risks
│                        │  • Next steps
│                        │  Latency: ~3s/thread
└──────┬─────────────────┘
       │
       │ Summary
       ▼
┌────────────────────────┐
│     Display UI         │  Show summary
└────────────────────────┘
       │
       │ User: "Reply to this"
       ▼
┌────────────────────────┐
│ Mail.ReplyDraft Agent  │  qwen2.5:14b
│                        │  • Context-aware
│                        │  • Tone: professional
│                        │  • Length: medium
│                        │  Latency: ~2s
└──────┬─────────────────┘
       │
       │ Draft email
       ▼
┌────────────────────────┐
│ HITL Approval          │  Human validates draft
│ (UI)                   │  Edit if needed
└──────┬─────────────────┘
       │
       │ Approved
       ▼
┌────────────────────────┐
│ Mail.Send Agent        │  Send via Gmail/Outlook API
│                        │  Log to audit trail
└──────┬─────────────────┘
       │
       │ Sent confirmation
       ▼
┌────────────────────────┐
│ RAG.Indexer            │  Index email content
│ (Background)           │  for future search
└────────────────────────┘
```

### 3.3 Flux Rédaction Académique

```
┌──────────────────────────────────────────────────────────────┐
│           FLUX RÉDACTION ACADÉMIQUE (Boucle Itérative)       │
└──────────────────────────────────────────────────────────────┘

User: "Write a 10-page research report on AI ethics"
      │
      ▼
┌────────────────────────┐
│ Writer Sub-Orchestrator│  Parse request
│                        │  Plan outline
└──────┬─────────────────┘
       │
       │ Outline + Notes
       ▼
┌────────────────────────┐
│ Writer.Academic Agent  │  qwen2.5:14b
│ (ITERATION 1)          │  Generate full draft
│                        │  • Introduction
│                        │  • Sections 1-5
│                        │  • Conclusion
│                        │  • References
│                        │  Latency: ~30s
└──────┬─────────────────┘
       │
       │ Draft v1
       ▼
    ┌──┴───────────────────────────────┐
    │                                  │
    ▼                                  ▼
┌──────────────────┐      ┌──────────────────┐
│Reviewer.         │      │Reviewer.         │
│Hallucination     │      │Citation          │
│Agent             │      │Agent             │
│                  │      │                  │
│Check:            │      │Check:            │
│• Internal        │      │• Format (APA)    │
│  consistency     │      │• DOI exists      │
│• Fact accuracy   │      │• Complete refs   │
│• Confidence      │      │                  │
│                  │      │                  │
│Latency: ~5s      │      │Latency: ~2s      │
└──────┬───────────┘      └──────┬───────────┘
       │                         │
       │ Issues found            │ Issues found
       ▼                         ▼
┌──────────────────────────────────────┐
│     Reviewer.Style Agent             │
│                                      │
│     Check:                           │
│     • Academic tone                  │
│     • Passive voice                  │
│     • Sentence length                │
│     • Paragraph structure            │
│                                      │
│     Latency: ~3s                     │
└──────┬───────────────────────────────┘
       │
       │ Combined issues report
       ▼
┌────────────────────────┐
│ Aggregated Issues      │  • 3 hallucinations detected
│                        │  • 2 citations incomplete
│                        │  • 5 style improvements
└──────┬─────────────────┘
       │
       │ IF issues > threshold
       ▼
┌────────────────────────┐
│ Writer.Academic Agent  │  Re-write problematic sections
│ (ITERATION 2)          │  Fix issues found by reviewers
│                        │  Latency: ~15s
└──────┬─────────────────┘
       │
       │ Draft v2
       ▼
┌────────────────────────┐
│ Reviewers (again)      │  Check fixes
│                        │  Latency: ~10s
└──────┬─────────────────┘
       │
       │ IF issues < threshold
       ▼
┌────────────────────────┐
│ Final Document         │  • Markdown
│ Export                 │  • PDF (via LaTeX)
│                        │  • Docx
└────────────────────────┘

Max iterations: 3
Total time (10 pages): ~2-3 minutes
```

### 3.4 Flux Recherche Web + Fact-Checking

```
┌──────────────────────────────────────────────────────────────┐
│            FLUX RECHERCHE WEB + FACT-CHECKING                 │
└──────────────────────────────────────────────────────────────┘

Agent needs info: "What is the current population of France?"
      │
      ▼
┌────────────────────────┐
│ Web.Search Agent       │  Query: "France population 2025"
│                        │
│ Engines:               │
│ • DuckDuckGo           │
│ • Brave Search         │
│ • SearxNG (local)      │
│                        │
│ Latency: ~2s           │
└──────┬─────────────────┘
       │
       │ Top 20 results (URLs + snippets)
       ▼
┌────────────────────────┐
│ Deduplicate & Rank     │  Remove duplicates
│                        │  Score by relevance
└──────┬─────────────────┘
       │
       │ Top 5 unique URLs
       ▼
   ┌───┴────┐
   │        │
   ▼        ▼ (parallel)
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Scrape│ │Scrape│ │Scrape│ │Scrape│ │Scrape│
│ URL1 │ │ URL2 │ │ URL3 │ │ URL4 │ │ URL5 │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
   │        │        │        │        │
   └────────┴────┬───┴────────┴────────┘
                 │
                 │ Clean text from all sources
                 ▼
┌────────────────────────┐
│ Web.FactChecker Agent  │  qwen2.5:14b
│                        │
│ Compare sources:       │
│ • Extract claims       │
│ • Find consensus       │
│ • Flag conflicts       │
│ • Score confidence     │
│                        │
│ Latency: ~5s           │
└──────┬─────────────────┘
       │
       │ Fact-check report
       ▼
┌────────────────────────┐
│ Result:                │
│                        │
│ Claim: "France pop     │
│         ~68M in 2025"  │
│                        │
│ Confidence: 95%        │
│                        │
│ Sources:               │
│ • insee.fr (official)  │
│ • worldbank.org        │
│ • wikipedia.org        │
│                        │
│ Consensus: TRUE        │
└──────┬─────────────────┘
       │
       │ Result + sources
       ▼
┌────────────────────────┐
│ RAG.Indexer            │  Index verified facts
│ (Background)           │  for future queries
└────────────────────────┘

Total time: ~10s
Confidence: HIGH (3+ trusted sources agree)
```

---

## 4. Stack Technique Détaillé

### Backend

```yaml
Language: Python 3.11+
Framework: FastAPI 0.109+

Dependencies:
  # Web
  - fastapi
  - uvicorn[standard]
  - websockets
  - python-multipart

  # Database
  - sqlalchemy
  - alembic
  - asyncpg
  - psycopg2-binary

  # Vector DB
  - qdrant-client

  # Redis
  - redis
  - aioredis

  # Task Queue
  - celery[redis]
  - flower  # Monitoring

  # AI/ML
  - ollama  # Client
  - sentence-transformers
  - langchain
  - langchain-community

  # Utils
  - pydantic
  - pyyaml
  - python-dotenv
  - httpx
  - aiofiles

  # Observability
  - opentelemetry-api
  - opentelemetry-sdk
  - opentelemetry-instrumentation-fastapi
  - prometheus-client

  # Security
  - python-jose[cryptography]
  - passlib[bcrypt]
  - cryptography

  # E-mail
  - google-auth
  - google-auth-oauthlib
  - google-api-python-client
  - msal  # Microsoft

  # WhatsApp
  - twilio

  # Testing
  - pytest
  - pytest-asyncio
  - pytest-cov
  - httpx-mock
```

### Frontend

```yaml
Language: TypeScript 5+
Framework: Next.js 14

Dependencies:
  # Core
  - next
  - react
  - react-dom

  # UI
  - tailwindcss
  - @shadcn/ui
  - lucide-react  # Icons
  - framer-motion  # Animations

  # État
  - zustand
  - swr

  # Forms
  - react-hook-form
  - zod

  # Charts
  - recharts
  - victory

  # Utils
  - axios
  - date-fns
  - clsx
  - tailwind-merge

  # WebSocket
  - socket.io-client

  # Audio
  - wavesurfer.js

  # Testing
  - vitest
  - @testing-library/react
  - playwright
```

### Infrastructure

```yaml
Containers: Docker + Docker Compose

Services:
  ollama:
    image: ollama/ollama:latest
    gpu: required (NVIDIA)
    memory: 16GB+ recommended

  postgres:
    image: postgres:16-alpine
    version: 16.1

  qdrant:
    image: qdrant/qdrant:latest
    version: 1.7+

  redis:
    image: redis:7-alpine
    version: 7.2

  minio:
    image: minio/minio:latest

  jaeger:
    image: jaegertracing/all-in-one:latest

  prometheus:
    image: prom/prometheus:latest

  grafana:
    image: grafana/grafana:latest
```

---

## 5. Base de Données

### PostgreSQL Schema

```sql
-- Agents
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(50) NOT NULL,
    kind VARCHAR(100) NOT NULL,
    skills JSONB NOT NULL DEFAULT '[]',
    owner_id UUID REFERENCES users(id),
    policy_id UUID REFERENCES policies(id),
    config JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'created',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Orchestrators
CREATE TABLE orchestrators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    scope VARCHAR(50) NOT NULL,
    max_agents INTEGER NOT NULL DEFAULT 10,
    rules JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Events (Audit Trail)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    source VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    agent_id UUID REFERENCES agents(id),
    user_id UUID REFERENCES users(id),
    payload JSONB NOT NULL DEFAULT '{}',
    indexed BOOLEAN DEFAULT FALSE
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kind VARCHAR(50) NOT NULL,
    title VARCHAR(500),
    path VARCHAR(1000),
    meta JSONB NOT NULL DEFAULT '{}',
    embedded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- E-mails
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    thread_id VARCHAR(255) NOT NULL,
    subject TEXT,
    body TEXT,
    from_email VARCHAR(255),
    to_emails JSONB,
    labels JSONB DEFAULT '[]',
    priority VARCHAR(20),
    theme VARCHAR(50),
    sentiment VARCHAR(20),
    received_at TIMESTAMP,
    indexed BOOLEAN DEFAULT FALSE,
    UNIQUE(account_id, thread_id)
);

-- Health Logs (Coach)
CREATE TABLE health_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    type VARCHAR(50) NOT NULL,  -- weight, calories_in, calories_out, activity
    value NUMERIC NOT NULL,
    unit VARCHAR(20),
    note TEXT,
    source VARCHAR(50) DEFAULT 'whatsapp'
);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kind VARCHAR(50) NOT NULL,  -- coach_daily, coach_weekly, meeting_cr
    period VARCHAR(50),
    path VARCHAR(1000),
    meta JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Templates
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- cr, email, academic
    format VARCHAR(20) NOT NULL,  -- markdown, latex, docx
    body TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'user',  -- admin, power_user, user
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Policies
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    rules JSONB NOT NULL DEFAULT '{}',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Qdrant Collections

```python
collections = [
    {
        "name": "agenticai_rag",
        "vector_size": 768,  # nomic-embed-text dimension
        "distance": "Cosine",
        "payload_schema": {
            "doc_id": "keyword",
            "chunk_id": "integer",
            "text": "text",
            "source": "keyword",
            "timestamp": "datetime"
        }
    },
    {
        "name": "voice_transcripts",
        "vector_size": 768,
        "distance": "Cosine",
        "payload_schema": {
            "session_id": "keyword",
            "speaker": "keyword",
            "timestamp": "datetime",
            "language": "keyword",
            "text": "text"
        }
    },
    {
        "name": "mail_threads",
        "vector_size": 768,
        "distance": "Cosine",
        "payload_schema": {
            "thread_id": "keyword",
            "account_id": "keyword",
            "subject": "text",
            "labels": "keyword[]",
            "received_at": "datetime"
        }
    }
]
```

---

**Suite dans le prochain message (Orchestration, Sécurité, Déploiement)...**

Veux-tu que je continue avec la suite de l'architecture ou tu as des questions sur ce que je viens de présenter?

## Cahier des charges – Assistant IA Agentique (v1.0)

Plateforme multi-agents 100% locale (LLM/embeddings/ASR via Ollama), extensible, pilotée par orchestrateurs, avec monitoring de la donnée, auto-évaluation, création de features par chat, et intégrations (mail, WhatsApp, écran, web).

---

### 1. Vision & périmètre
- Objectif : bâtir un assistant « agentique » modulaire où chaque feature = 1..n agents spécialisés, coordonnés par des sous-orchestrateurs et un orchestrateur master.
- Principe : l’orchestration crée/ajuste/supprime des agents de façon autonome, sur la base des métriques (qualité, latence, dérive) et des politiques.
- Expérience : tout démarre par WhatsApp ou le chat web. L’utilisateur décrit son besoin → le système conçoit, propose, implémente (avec tests) → l’IHM s’actualise.
- Contrainte clé : modèles IA locaux via Ollama (LLM/embeddings/whisper). Connecteurs autorisés : Gmail/Outlook/WhatsApp/Calendriers/Drive internes si nécessaires.

### 2. Cas d’usage prioritaires
1. Réunion temps réel : capture audio → transcription (ASR), traduction live, Q&A avec RAG minute-par-minute, marqueurs « Action/Décision ».
2. E-mail : ingestion + classement + synthèse + rédaction + envoi (HITL).
3. Chat agentique : commandes naturelles pour créer agents/UI/workflows/tests.
4. Coach Santé : logs via WhatsApp (kcal/poids/sport) → reporting & recommandations.
5. Comptes-rendus (CR) : à partir de transcript/puces → template (MD/LaTeX/Docx).
6. Capture d’écran : OCR + compréhension de contexte + overlays (traduire, résumer, extraire).
7. Web Intelligence (nouveau) : collecte d’infos utiles sur Internet pour nourrir tous les agents, avec citations et contrôle de conformité.
8. Rédacteur académique (nouveau) : mémoire/rapports académiques avec agent de relecture anti-hallucinations & vérifications croisées.
9. PM IT (nouveau) : copilote chef de projet (rituels agiles, risques, RCAs, RACI, reporting CODIR, planning…).

### 3. Architecture (vue d’ensemble)
- Interface : Web (Next.js/React ou Django+HTMX), widget réunion live, bot WhatsApp.
- Orchestration : Orchestrateur master + sous-orchestrateurs par domaine (Voix, Mail, RAG/Chat, Santé, CR, WebIntel, PM).
- Agents : micro-services spécialisés (stateless), déclarés dans un Registry.
- IA locale : Ollama (LLM/embeddings), whisper pour ASR, OCR local.
- Données : PostgreSQL (état), Qdrant/Chroma (vecteurs), MinIO (fichiers).
- Messaging : NATS ou Redis Streams.
- Workers/Workflows : Celery/Temporal/Prefect.
- Observabilité : OpenTelemetry, dashboards, journaux structurés.
- Sécurité : RBAC, Vault secrets, chiffrement, audit trail.

### 4. Orchestration & gouvernance
- Orchestrateur master : priorisation globale, arbitrage ressources, application des politiques (quotas, garde-fous).
- Sous-orchestrateurs : portés par domaine, traduisent une demande en plan d’exécution (graphes), peuvent proposer la création d’agents/UI/tests.
- Garde-fous : quotas de création d’agents, autorisations par scope, HITL pour actions sensibles (envoi mail externe, partage document, changement de politique).
- Traçabilité : chaque décision d’orchestration est expliquée (inputs → plan → résultats), consultable dans l’IHM.

### 5. Agents (exemples par domaine)
- Voix : Voice.Capture, Voice.Transcribe (whisper), Voice.Translate, Voice.QA (RAG), Voice.Summarizer.
- E-mail : Mail.Ingest (OAuth), Mail.Classify, Mail.Summarize, Mail.ReplyDraft, Mail.Sender (HITL), Mail.ThreadIndexer.
- RAG/Chat : RAG.Indexer, RAG.Searcher, Chat.Router, Chat.AgentCreator.
- Santé : Coach.LogIngest, Coach.Analyst, Coach.Reporter, Coach.Recommender.
- CR/Docs : CR.Builder, CR.DecisionExtractor, Docs.Formatter (LaTeX/Docx), Docs.Citer (citations/biblio), Docs.PlagiarismLocal.
- Screen : Screen.Capture, Screen.OCR, Screen.Context, Screen.Overlay.
- Web Intelligence : Web.Crawler, Web.Focuser (requêtes ciblées), Web.Extractor (schémas), Web.FactChecker, Web.CitationStore.
- PM IT : PM.StandupSummarizer, PM.RiskMiner, PM.DependencyGrapher, PM.BurnupCoach, PM.RACI.Suggester, PM.Report.CODIR, PM.ScopeImpact, PM.Retros.Analyst.

### 6. Flux majeurs (séquences cibles)

#### 6.1 Réunion Teams – transcription/traduction/Q&A live
1. Voice.Capture → paquets audio 1–2 s (VAD).
2. Voice.Transcribe (whisper local) → texte horodaté.
3. Voice.Translate → langue cible.
4. RAG.Indexer ingère au fil de l’eau.
5. Voice.QA répond via chat (citations avec timecodes).
6. Export transcript + chapitrage + marqueurs.

#### 6.2 E-mail – ingestion → synthèse → réponse
1. Mail.Ingest (Gmail/Outlook, scopes minimaux).
2. Mail.Classify (priorité, thème).
3. Mail.Summarize (bullets, risques, next steps).
4. Mail.ReplyDraft → validation humaine → Mail.Sender.
5. Indexation utile (RAG) + métriques monitoring.

#### 6.3 Chat → Feature/Agent/UI (création naturelle)
- L’utilisateur décrit. Chat.AgentCreator génère la spec (agents, endpoints, tests, widgets, KPIs).
- Builder.Orchestrator déploie et exécute les tests.
- L’IHM se met à jour (hot-reload composants).

#### 6.4 Coach Santé via WhatsApp
- Coach.LogIngest parse messages libres (kcal/poids/sport).
- Coach.Analyst calcule bilans et tendances.
- Coach.Reporter publie quotidien/hebdo/mensuel.
- Coach.Recommender alerte et propose des ajustements.

#### 6.5 CR & documents
- Input : transcript/puces/sources.
- CR.Builder + Docs.Formatter → PDF/LaTeX/MD/Docx.
- Docs.Citer gère bibliographie (BibTeX/CSL).
- Docs.Reviewer (anti-hallucinations) valide les assertions avec preuves.

#### 6.6 Web Intelligence
- Web.Focuser reçoit un besoin (« cartographier subventions IA Maroc 2024–2025 »).
- Web.Crawler collecte (robots.txt, rate-limit).
- Web.Extractor structure (titres, auteurs, dates, passages clés).
- Web.FactChecker confronte sources, score confiance.
- Web.CitationStore garde URLs/extraits + hash.
- Résumés & alertes vers agents consommateurs (RAG, CR, PM).

### 7. IHM (exigences)
- Dashboard par domaine (Réunions, E-mails, Santé, Docs, WebIntel, PM).
- Panneau live (sous-titres, langue, marqueurs Action/Décision).
- Chat latéral (RAG + commandes agentiques).
- Boîte d’envoi (Brouillon/Relecture/Envoi).
- Rapports Santé : courbes, heatmaps, objectifs.
- WebIntel : carte sources, extraits, citations.
- PM : risques, burndown/burnup, dépendances (graph), décisions, RAID log.
- Styles : sombre/clair, responsive, accessibilité.

### 8. Monitoring & Data Quality
- Ce qu’on mesure : complétude, duplicats, schéma, dérive sémantique (embeddings), latence, WER, précision classif, faithfulness RAG, satisfaction (ratings).
- Pipeline : Monitor.Collector → Monitor.Validator → Monitor.Drift → Monitor.Insights → Monitor.ActionPlanner.
- Actions auto : A/B tests, changement de modèle, création d’agent de mitigation, retuning chunking RAG, ré-indexation ciblée.
- Règles (YAML) paramétrables par domaine.

### 9. Auto-évaluation, A/B tests & sélection de modèles
- Golden sets versionnés par domaine.
- AB tests déclenchés automatiquement si KPI < seuil.
- Canary (10%) → promotion si > baseline.
- Politiques modèles : candidats par tâche, contraintes (latence, VRAM), forbid cloud.
- Journalisation de tous les switchs et motifs.

### 10. Choix du LLM par agent/orchestrateur
- UI : sélection LLM primaire, fallbacks, profil (qualité/latence).
- Overrides par sous-tâche (ex. traduction vs synthèse).
- Auto-switch sur violation SLA récurrente.

### 11. Web Intelligence – exigences détaillées (nouveau)
- Collecte : headless browser local, respect robots.txt, user-agent dédié, rate-limit, cache.
- Extraction : parse HTML/PDF (screenshot → OCR si besoin), normalisation (titres, auteurs, dates, résumé, passages).
- Éthique & conformité : citer les sources, stocker hash/URL/date, éviter contenus protégés non citables, filtres NSFW.
- Anti-hallucinations : toute affirmation issue du web doit lier au passage source.
- API : /webintel/query, /webintel/brief, /webintel/corpus/{topic}.
- Intégration : agents consommateurs (Docs, PM, CR, RAG) reçoivent briefs sourcés.

### 12. Rédacteur académique & relecteur anti-hallucinations (nouveau)
- Pipeline :
  1. Scoping (objectif, audience, normes, bibliostyle),
  2. Plan guidé (titres, hypothèses, contributions),
  3. Draft sectionné (chaque paragraphe avec preuves liées),
  4. Citations (BibTeX/CSL),
  5. Relecture (style, cohérence, anti-plagiat local),
  6. Vérification factuelle par Docs.Reviewer (liens vers sources),
  7. Compilation (LaTeX/PDF/Docx),
  8. Check final (liste de contrôle).
- Agents : Docs.Outliner, Docs.Drafter, Docs.Citer, Docs.Reviewer, Docs.Style, Docs.Compiler.
- Exigence majeure : toute assertion doit pointer vers une preuve (source interne/externe) ; sinon marquée à vérifier.
- Sorties : version longue + exécutive, annexes (tableaux/figures), bibliographie.

### 13. Copilote PM IT (nouveau)
- Rituels : standups auto-résumés, minutes de meetings, décisions, actions.
- Risques : PM.RiskMiner scanne mails/notes/tickets → heatmap risques + plans de mitigation.
- Dépendances : PM.DependencyGrapher (tickets/epics) → graph interactif.
- Charges & avancement : burndown/burnup, vélocité, WIP, prédictions simples.
- Reporting : CODIR pack (tableau de bord + commentaires générés).
- Gouvernance : RACI suggéré, gestion des décisions (registre), Scope Impact (analyse des changements).
- Intégrations : Jira/Azure DevOps/YouTrack (API), Calendrier, Drive.
- Commandes (chat) : “prépare la note de cadrage”, “crée le plan de comms”, “simule l’impact d’un staff-down de 20%”.

### 14. API (extraits)
- POST /voice/session, WS /voice/stream, GET /voice/live, POST /voice/bookmark.
- POST /mail/summarize, POST /mail/reply, POST /mail/send (HITL).
- POST /coach/log, GET /coach/report?period=week.
- POST /cr/build, POST /docs/compile.
- POST /agents/create, GET /agents, DELETE /agents/{id}.
- POST /orchestrator/policy, GET /trace/{id}.
- POST /webintel/query, GET /webintel/brief.
- POST /pm/risks/analyze, GET /pm/report/codir.

### 15. Données & schémas (principal)
- agents(id, name, kind, skills[], owner, policy_id, status, created_at)
- orchestrators(id, scope, max_agents, rules_json)
- events(id, ts, source, type, payload_json)
- documents(id, kind, path, meta_json, embedded)
- vectors(id, doc_id, chunk_id, embedding, meta)
- emails(account_id, thread_id, meta, body, labels[])
- health_logs(ts, type, value, note)
- reports(id, kind, period, path, meta)
- templates(id, name, format, body, variables[])
- evaluations(id, agent_id, dataset_id, metric, value, ts)
- ab_tests(id, scope, candidates[], winner, metrics_json, ts)
- proposals(id, kind, detail_json, status, created_by, ts)
- screenshots(id, path, ocr_text, app, title, meta_json, ts)
- citations(id, doc_id, url, hash, title, author, date, snippet)

### 16. Sécurité & conformité
- Données locales par défaut, secrets en Vault, chiffrement au repos/en transit.
- RBAC (Admin/Power user/User), audit trail (toutes actions sensibles).
- Masquage PII sur captures d’écran (côté client).
- Politique WhatsApp : opt-in clair, logs consultables, suppression à la demande.
- Journalisation des accès API (mail, calendriers, Jira, etc.).

### 17. KPI, SLA & objectifs qualité
- Voix : WER ≤ 18% (calme), latence phrase-à-phrase ≤ 3 s, traduction +1 s max.
- E-mail : précision classif ≥ 87%, synthèse < 3–5 s, satisfaction ≥ 4/5.
- RAG : P@1 ≥ 75%, réponses citées ≥ 95%.
- Docs : conformité style ≥ 95%, assertions non sourcées = signalées.
- WebIntel : 100% éléments clés citables (URL + extrait).
- PM : couverture décisions ≥ 90%, délais minutes < 10 min.

### 18. Tests & qualité
- Unitaires par agent, contrats connecteurs, intégration par domaine.
- Non-régression sur golden sets (Voix, E-mail, RAG, Docs, PM).
- Tests agentiques (création dynamique, quotas, garde-fous).
- Sécurité (scopes, RBAC, chiffrement).
- Performance (latence, throughput, VRAM).

### 19. Déploiement & opérations
- Docker Compose (Ollama + API + DB + VectorDB + MinIO + Redis/NATS + Front).
- Profils CPU/GPU (whisper/LLM), volumes chiffrés, backups & restauration.
- Mise à jour modèles par tags versionnés, rollback possible.

### 20. Politiques d’orchestration (exemple YAML)
```yaml
orchestrator:
  max_concurrent_agents: 12
  creation_rate_limit_per_min: 3
  guarded_actions: ["send_email_external", "share_file", "change_policies"]
  require_human_approval: ["send_email_external", "create_sub_orchestrator"]
models_policy:
  default_llm_candidates: ["llama3:8b-instruct", "qwen2.5:7b-instruct", "mistral:7b-instruct"]
  embedding: "nomic-embed-text"
  constraints:
    forbid_cloud: true
    max_vram_gb: 10
monitoring:
  rag:
    p_at_1_min: 0.75
    actions_if_breach: ["enable_hybrid_search", "increase_chunk_size", "ab_test_models"]
  asr:
    max_wer: 0.18
    max_latency_ms: 3000
    actions_if_breach: ["switch_whisper_variant", "noise_suppression"]
  email_classification:
    target_precision: 0.87
    auto_mitigations:
      - if: "precision < 0.80"; then: "create_agent: Mail.PriorityBooster"
      - if: "precision between 0.80 and 0.87"; then: "enable_ab_test: ['llama3','qwen2.5']"
```

### 21. Roadmap (8 semaines)
- S1–S2 : Monitoring core + dashboards ; policies modèles ; skeleton A/B.
- S3 : Chat→Feature (Designer/Builder) + UI hot-reload.
- S4 : WhatsApp Router + Coach complet.
- S5 : Screen Intelligence (capture + OCR + overlay).
- S6 : Web Intelligence (crawler + fact-check + citations).
- S7 : Rédacteur académique + Reviewer anti-hallucinations.
- S8 : Copilote PM (risques, décisions, reporting) + durcissement sécu.

### 22. Livrables
- OpenAPI (API), schemas DB + migrations, registry agents (YAML).
- Policies (monitoring, modèles), golden sets (Voix/E-mail/RAG/Docs/PM).
- Templates CR/Docs (LaTeX/MD/Docx), exemples de prompts.
- Playbooks (opérations, sauvegardes, MAJ modèles).
- Tableaux de bord (latence, WER, précision, dérive, adoption).
- Guide utilisateur (chat→feature, WhatsApp, UI widgets).

### 23. Non-fonctionnels
- Disponibilité locale ≥ 99%.
- TTM “chat→prod” petit agent/UI < 10 min.
- Performances : objectifs section KPI.
- Évolutivité : ajout d’agents sans arrêt global (rolling).
- Portabilité : Linux/Windows/macOS, GPU facultatif (recommandé).
- Sécu : RBAC, chiffrement, audit complet.

### 24. Annexes

#### 24.1 Exemples de commandes (chat)
- « Ajoute un agent qui extrait les to-dos dans mes mails, crée un widget ‘To-Do Inbox’, et envoie chaque matin à 8h un rappel. »
- « Prépare un CR exécutif de la réunion d’aujourd’hui avec sections Décisions/Actions/Risques, export PDF. »
- « Sur Mail.Summarize, lance un A/B llama3 vs qwen2.5 pendant 3 jours. »
- « WebIntel : fais un brief sourcé sur ‘subventions IA au Maroc 2025’ avec 5 sources fiables. »
- « PM : génère un RACI pour le projet ADV Email Assistant et propose un plan de com. »

#### 24.2 Grille de relecture (anti-hallucinations)
- Assertion ↔ preuve ? (URL interne/externe ou citation RAG).
- Style conforme ? (norme académique adoptée).
- Chiffres & dates cohérents ?
- Plagiat local ? Similarité < seuil.

#### 24.3 Templates (extrait CR)
- Contexte | Décisions | Actions (Owner, Due) | Risques | Annexes | Liens.

### 25. À valider
- Choix stack UI (Next.js/React vs Django+HTMX).
- Vector DB (Qdrant vs Chroma).
- Liste modèles Ollama (LLM + embeddings + whisper variante).
- Fréquence des recommandations (quotidien 18:00 ? hebdo ven 17:00 ?).
- Seuils initiaux monitoring par domaine.
- Intégrations PM (Jira/Azure DevOps/YouTrack) et comptes e-mail.

Fin v1.0.
