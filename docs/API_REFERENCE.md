# AgenticAI V4 – Référence API

> Toutes les routes sont disponibles sous `http://localhost:8000`. Les appels nécessitant un déclenchement d’orchestrateur renvoient un `trace_id` consultable via `GET /api/orchestrator/trace/{id}`.

## Sommaire

1. [Voix temps réel](#voix-temps-réel)
2. [E-mail](#e-mail)
3. [RAG & Chat](#rag--chat)
4. [Coach Santé](#coach-santé)
5. [Docs & CR](#docs--cr)
6. [Web Intelligence](#web-intelligence)
7. [PM Copilote](#pm-copilote)
8. [Agents & Orchestration](#agents--orchestration)
9. [Monitoring](#monitoring)

---

## Voix temps réel

### POST `/api/voice/session`
- **Description** : Démarre une session de réunion (flux audio côté WebSocket).
- **Body**
  ```json
  {
    "meeting_id": "mtg-2025-01-01",
    "language": "fr",
    "translation_language": "en"
  }
  ```
- **Réponse**
  ```json
  {
    "session_id": "uuid",
    "status": "accepted",
    "created_at": "2025-01-26T18:42:00Z"
  }
  ```

### POST `/api/voice/bookmark`
- **Description** : Ajoute un marqueur “Action” ou “Décision”.
- **Body**
  ```json
  { "session_id": "uuid", "label": "Action", "timestamp": 123.4 }
  ```

### WebSockets
- `/ws/voice` : flux audio -> transcriptions (JSON)
- `/ws/chat` : commandes agentiques (JSON `{ "message": "..." }`)

---

## E-mail

### POST `/api/mail/summarize`
- **Body** : `{ "account_id": "me", "thread_id": "abcd" }`
- **Réponse** : `summary`, `risks`, `next_steps`

### POST `/api/mail/reply`
- **Body** : `{ "account_id": "...", "thread_id": "...", "instructions": "..." }`
- **Réponse** : brouillon (`draft`), flag `requires_hitl`

### POST `/api/mail/send`
- Déclenche un envoi (HITL) – garde-fou orchestrateur

---

## RAG & Chat

### POST `/api/rag/search`
- **Body** : `{ "query": "...", "top_k": 5 }`
- **Réponse** : liste de passages (`text`, `score`, `source`)

### POST `/api/rag/ingest`
- Ingestion d’un document (stub → `status: indexed`)

---

## Coach Santé

### POST `/api/coach/log`
- **Body** : `{ "user_id": "user123", "metric": "calories", "value": 1800 }`
- **Réponse** : `stored`, `trace_id`

### GET `/api/coach/report`
- Paramètres : `user_id`, `period`
- **Réponse** : logs agrégés (fallback mémoire)

---

## Docs & CR

### POST `/api/docs/cr/build`
- **Body** : `{ "meeting_id": "mtg", "sections": ["Decisions","Actions"] }`
- **Réponse** : `document_id`, `trace_id`

### POST `/api/docs/compile`
- **Body** : `{ "doc_id": "cr-id", "format": "pdf" }`
- **Réponse** : chemin de l’artefact

---

## Web Intelligence

### POST `/api/webintel/query`
- **Body** : `{ "topic": "subventions IA Maroc 2025", "sources_min": 5 }`
- **Réponse** : `verdicts` (fact-check)

### GET `/api/webintel/brief`
- Résumé/mémo (placeholder)

---

## PM Copilote

### POST `/api/pm/risks/analyze`
- **Body** : `{ "project_id": "proj", "sources": ["jira", "mails"] }`
- **Réponse** : liste de risques, `trace_id`

### GET `/api/pm/report/codir`
- **Query** : `project_id`, `sprint`
- **Réponse** : sections de compte-rendu (stub)

---

## Agents & Orchestration

### GET `/api/agents`
- Liste des agents enregistrés (registry mémoire)

### POST `/api/agents`
- Crée un agent custom (status `draft`)

### DELETE `/api/agents/{id}`
- Marque l’agent comme `retired`

### POST `/api/orchestrator/policy`
- Met à jour la politique active (max agents, garde-fous…)

### GET `/api/orchestrator/trace/{id}`
- Retourne le plan, les exécutions et résultats (persistés en mémoire/fallback)

---

## Monitoring

### GET `/api/monitoring/insights`
- Tableau d’insights (stub – vide par défaut)

---

## Codes réponse

- `202 Accepted` pour les triggers orchestrateur lorsque le plan est accepté.
- `200 OK` pour les endpoints CRUD.
- `4xx` pour erreurs de validation ou actions non autorisées (garde-fous).
- `500` géré par le handler global (trace loggée).

---

## Authentification

- À définir : JWT locaux / OAuth2 selon intégrations (placeholder).

---

## Notes

- Les services externes (Ollama, Postgres, Qdrant, Redis) possèdent un fallback mémoire pour faciliter le dev local.
- Les `trace_id` sont essentiels pour l’audit trail et la traçabilité dans l’IHM.

