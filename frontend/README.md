# AgenticAI V4 - Frontend

Interface utilisateur React pour AgenticAI V4

## Stack Technique

- **React 18** - Framework UI
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Axios** - HTTP client
- **React Router** - Navigation
- **Lucide React** - Icons

## Installation

```bash
npm install
```

## Développement

```bash
npm run dev
```

L'application sera disponible sur http://localhost:3000

## Build de production

```bash
npm run build
```

Les fichiers buildés seront dans le dossier `dist/`

## Configuration

Créez un fichier `.env` avec:

```bash
VITE_API_URL=http://localhost:8000
```

## Pages disponibles

### Authentification
- `/login` - Connexion
- `/register` - Inscription

### Application
- `/dashboard` - Vue d'ensemble avec statistiques
- `/agents` - Gestion des agents (CRUD)
- `/documents` - Upload et recherche de documents
- `/chat` - Interface de chat avec les agents

## Fonctionnalités

### Authentification
- Connexion avec JWT
- Inscription de nouveaux utilisateurs
- Protection des routes privées
- Gestion automatique des tokens

### Dashboard
- Statistiques utilisateur (agents, documents, stockage, requêtes)
- Informations système
- Actions rapides

### Agents
- Liste de tous les agents (système + personnalisés)
- Création d'agents personnalisés
- Suppression des agents personnalisés
- Affichage des compétences et métadonnées

### Documents
- Upload de documents (PDF, DOCX, TXT, MD, HTML)
- Liste des documents uploadés
- Recherche sémantique avec reranking
- Suppression de documents

### Chat
- Interface de chat en temps réel
- Messages utilisateur/assistant
- Indicateur de saisie

## Architecture

```
frontend/
├── src/
│   ├── components/       # Composants réutilisables
│   │   └── Layout.tsx   # Layout principal avec sidebar
│   ├── pages/           # Pages de l'application
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── AgentsPage.tsx
│   │   ├── DocumentsPage.tsx
│   │   └── ChatPage.tsx
│   ├── services/        # Services API
│   │   └── api.ts      # Client axios configuré
│   ├── store/          # State management
│   │   └── authStore.ts # Store Zustand pour l'auth
│   ├── types/          # TypeScript types
│   │   └── index.ts    # Types partagés
│   ├── styles/         # CSS global
│   │   └── index.css   # Tailwind + styles custom
│   ├── App.tsx         # Composant racine
│   └── main.tsx        # Point d'entrée
├── index.html          # Template HTML
├── vite.config.ts      # Configuration Vite
├── tailwind.config.js  # Configuration Tailwind
└── tsconfig.json       # Configuration TypeScript
```

## Connexion par défaut

```
Email: admin@agenticai.dev
Password: admin123
```

## API Backend

Le frontend communique avec le backend FastAPI via:
- Base URL: `http://localhost:8000`
- Auth: JWT Bearer token dans l'en-tête Authorization
- Proxy Vite pour éviter les problèmes CORS

## Notes

- Le chat est en mode démonstration pour l'instant
- WebSocket sera ajouté dans une prochaine version
- Toutes les routes nécessitent une authentification sauf `/login` et `/register`
