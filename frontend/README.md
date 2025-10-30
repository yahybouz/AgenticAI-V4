# Frontend AgenticAI V4 (Next.js 14) – Roadmap

## Objectifs

1. **Dashboard multi-domaines** : panneaux Voix / E-mail / Santé / Docs / WebIntel / PM avec cartes KPI.
2. **Widget réunion live** : sous-titres en temps réel, traduction, marqueurs “Action/Décision”.
3. **Chat agentique** : commandes naturelles (création d’agents, requêtes RAG) + réponses citées.
4. **Boîte d’envoi HITL** : validation des drafts e-mail, envoi planifié.
5. **Observabilité** : graphiques latence, WER, dérive, satisfaction.

## Stack prévue

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS + shadcn/ui**
- **Zustand** pour l’état client
- **TanStack Query** pour la data fetch
- **Socket.io client** pour `/ws/chat` et `/ws/voice`

## Structure cible

```
frontend/
├── app/
│   ├── (dashboard)/             # route principale
│   ├── (auth)/                  # login, RBAC
│   ├── api/                     # actions server components
│   └── layout.tsx
├── components/
│   ├── charts/                  # modules graphiques
│   ├── voice/                   # meeting widget
│   ├── mail/                    # inbox HITL
│   ├── rag-chat/                # chat agentique
│   └── shared/                  # UI générique
├── lib/
│   ├── api.ts                   # client REST
│   ├── sockets.ts               # wrapper WebSocket
│   └── stores/                  # Zustand stores
└── public/
    └── icons/
```

## Backlog (ordre recommandé)

1. **Initialisation** (`pnpm create next-app --ts`) + Tailwind.
2. **Layout + thème** (dark/light, shadcn/ui).
3. **Page Dashboard** avec tuiles KPI (données mockées, puis API).
4. **Composant voix live** : sous-titres en streaming depuis `/ws/voice`.
5. **Chat agentique** : conversation, commandes, citations.
6. **Inbox mail HITL** : statuts, approbation envoi (`/api/mail/*`).
7. **Monitoring** : graphiques via API `/api/monitoring/insights`.
8. **Auth & RBAC** : mocks → intégration OAuth2 interne.

## Intégration API

- Utiliser `NEXT_PUBLIC_API_BASE` pour pointer vers FastAPI.
- Les WebSocket peuvent être bridgés via `/api/socket` (route Next) ou directement `ws://localhost:8000/ws/...`.

## Tests & Qualité

- **Playwright** pour E2E (tests flows Voix, Mail, Chat).
- **Jest/Testing Library** pour composants critiques.
- **Storybook** pour itérer sur les widgets.

---

> Cette documentation sert de guide avant la mise en place du scaffold Next.js. Elle garantit la cohérence avec le cahier des charges et le backend déjà disponible.

