# 🧪 Guide de Test - AgenticAI V4

**Version:** 4.0.0
**Date:** 31 octobre 2025

Ce guide vous permet de tester toutes les fonctionnalités disponibles de l'application.

---

## 🚀 Avant de Commencer

### Vérifier que les Services Tournent

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl -s http://localhost:3001 > /dev/null && echo "✅ Frontend OK"

# Ollama
ollama list
```

### URLs d'Accès

- **Application Web:** http://localhost:3001
- **API Documentation:** http://localhost:8000/docs
- **Backend API:** http://localhost:8000

### Identifiants par Défaut

```
Email:    admin@agenticai.dev
Password: admin123
```

---

## 📋 Tests à Effectuer

### 1. Test de Connexion (Authentification)

**Objectif:** Vérifier que l'authentification JWT fonctionne

#### Via Interface Web

1. Ouvrir http://localhost:3001
2. Remplir le formulaire de connexion :
   - Email: `admin@agenticai.dev`
   - Password: `admin123`
3. Cliquer sur "Se connecter"
4. **Résultat attendu:** Redirection vers le Dashboard

#### Via API

```bash
# Login et récupération du token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agenticai.dev","password":"admin123"}' | python3 -m json.tool

# Sauvegarder le token
TOKEN="votre-token-ici"

# Tester l'accès à une route protégée
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/auth/me | python3 -m json.tool
```

**Résultat attendu:**
```json
{
  "id": "79322da5-d4c5-487b-8a18-a74788c20d98",
  "email": "admin@agenticai.dev",
  "username": "admin",
  "role": "admin",
  "status": "active"
}
```

---

### 2. Test du Dashboard (Statistiques Utilisateur)

**Objectif:** Vérifier l'affichage des statistiques et quotas

#### Via Interface Web

1. Après connexion, observer le Dashboard
2. Vérifier les cartes affichées :
   - Nombre d'agents créés
   - Nombre de documents uploadés
   - Utilisation du stockage
   - Quota disponible

**Résultat attendu:** Affichage correct des statistiques

#### Via API

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/auth/me/stats | python3 -m json.tool
```

**Résultat attendu:**
```json
{
  "agents_count": 0,
  "documents_count": 0,
  "storage_used_mb": 0,
  "max_agents": 10,
  "max_documents": 1000,
  "max_storage_mb": 5000
}
```

---

### 3. Test de la Liste des Agents

**Objectif:** Vérifier l'affichage des 19 agents disponibles

#### Via Interface Web

1. Cliquer sur "Agents" dans le menu latéral
2. Observer la liste des agents affichés
3. Vérifier les informations :
   - Nom de l'agent
   - Domaine (chat, coach, docs, mail, pm, rag, voice, webintel)
   - Compétences (skills)
   - Modèle LLM utilisé

**Résultat attendu:** Affichage de 19 agents organisés par domaine

#### Via API

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/agents/ | python3 -m json.tool
```

**Résultat attendu:** Liste JSON de tous les agents avec leurs propriétés

---

### 4. Test de Création d'Agent

**Objectif:** Créer un agent personnalisé

#### Via Interface Web

1. Sur la page "Agents", cliquer sur "Créer un Agent"
2. Remplir le formulaire :
   - **Nom:** "Mon Agent de Test"
   - **Domaine:** chat
   - **Modèle:** qwen2.5:14b
   - **Compétences:** summarization
   - **Description:** "Agent créé pour tester la création"
3. Cliquer sur "Créer"

**Résultat attendu:** Agent créé et visible dans la liste

#### Via API

```bash
curl -X POST http://localhost:8000/api/agents/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TestAgent",
    "domain": "chat",
    "model": "qwen2.5:14b",
    "skills": ["summarization"],
    "description": "Agent de test via API",
    "input_schema": {},
    "output_schema": {}
  }' | python3 -m json.tool
```

**Résultat attendu:** Agent créé avec ID unique

---

### 5. Test de Génération d'API Key

**Objectif:** Générer une clé API pour l'utilisateur

#### Via Interface Web

1. Aller dans "Paramètres" ou "Profil"
2. Section "API Key"
3. Cliquer sur "Générer une nouvelle clé"
4. Copier la clé générée

**Résultat attendu:** Clé API générée et affichée

#### Via API

```bash
curl -X POST http://localhost:8000/api/auth/me/api-key \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**Résultat attendu:**
```json
{
  "api_key": "agenticai_abc123xyz...",
  "created_at": "2025-10-31T14:00:00"
}
```

---

### 6. Test des Formats de Documents

**Objectif:** Voir les formats de documents supportés

#### Via Interface Web

1. Aller sur "Documents"
2. Observer la section "Formats supportés"

**Résultat attendu:** Liste des formats (.pdf, .docx, .txt, .md, .json, .csv)

#### Via API

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/documents/formats | python3 -m json.tool
```

**Résultat attendu:**
```json
{
  "formats": [
    {"extension": ".pdf", "description": "PDF documents"},
    {"extension": ".docx", "description": "Word documents"},
    {"extension": ".txt", "description": "Text files"},
    {"extension": ".md", "description": "Markdown files"},
    {"extension": ".json", "description": "JSON files"},
    {"extension": ".csv", "description": "CSV files"}
  ]
}
```

---

### 7. Test du Cache de Documents

**Objectif:** Vérifier les statistiques du cache

#### Via API

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/documents/cache/stats | python3 -m json.tool
```

**Résultat attendu:**
```json
{
  "entries": 0,
  "size_mb": 0,
  "hit_rate": 0
}
```

---

### 8. Test du Monitoring

**Objectif:** Voir les métriques système

#### Via Interface Web

1. Aller sur "Monitoring" (si disponible)
2. Observer les métriques affichées

#### Via API

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/monitoring/insights | python3 -m json.tool
```

**Résultat attendu:** Métriques système (CPU, RAM, disque, agents actifs)

---

### 9. Test de Création de Compte

**Objectif:** Créer un nouveau compte utilisateur

#### Via Interface Web

1. Se déconnecter (si connecté)
2. Cliquer sur "Créer un compte"
3. Remplir le formulaire :
   - **Email:** test@example.com
   - **Username:** testuser
   - **Password:** testpass123 (min 8 caractères)
4. Cliquer sur "S'inscrire"

**Résultat attendu:** Compte créé, redirection vers login

#### Via API

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "securepass123"
  }' | python3 -m json.tool
```

**Résultat attendu:**
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "username": "newuser",
  "role": "user",
  "status": "active"
}
```

---

### 10. Test de l'Interface Chat (Si disponible)

**Objectif:** Tester la conversation avec l'orchestrateur

#### Via Interface Web

1. Aller sur "Chat"
2. Taper un message : "Bonjour, qui es-tu ?"
3. Envoyer
4. Observer la réponse

**Résultat attendu:** Réponse de l'orchestrateur multi-agents

---

## 🐳 Tests Avancés (Nécessitent Docker)

### Prérequis

```bash
# Démarrer Docker Desktop
open -a Docker

# Attendre que Docker soit prêt
docker ps

# Lancer les services
cd /Users/yahybouz/Desktop/Mes\ Scripts/AgenticAI-V4
docker compose up -d
```

### 11. Test d'Upload de Documents (RAG)

**Objectif:** Uploader un document et l'indexer avec Qdrant

#### Via Interface Web

1. Aller sur "Documents"
2. Cliquer sur "Upload Document"
3. Sélectionner un fichier (PDF, DOCX, TXT, MD)
4. Choisir une collection : "documents"
5. Cliquer sur "Upload"

**Résultat attendu:** Document uploadé et indexé

#### Via API

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "collection=documents" | python3 -m json.tool
```

---

### 12. Test de Recherche Sémantique (RAG)

**Objectif:** Effectuer une recherche dans les documents indexés

#### Via Interface Web

1. Sur "Documents", utiliser la barre de recherche
2. Taper une requête : "What is AgenticAI?"
3. Observer les résultats

**Résultat attendu:** Documents pertinents avec scores de similarité

#### Via API

```bash
curl -X POST http://localhost:8000/api/documents/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is AgenticAI?",
    "top_k": 5,
    "enable_reranking": true
  }' | python3 -m json.tool
```

---

### 13. Test d'Ingestion RAG

**Objectif:** Indexer des documents dans Qdrant

#### Via API

```bash
curl -X POST http://localhost:8000/api/rag/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "AgenticAI is a multi-agent AI system...",
    "metadata": {"source": "manual", "type": "documentation"},
    "collection": "knowledge_base"
  }' | python3 -m json.tool
```

---

### 14. Test de Recherche RAG

**Objectif:** Recherche sémantique avec contexte

#### Via API

```bash
curl -X POST http://localhost:8000/api/rag/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How does the multi-agent system work?",
    "collection": "knowledge_base",
    "top_k": 3
  }' | python3 -m json.tool
```

---

## 🧪 Tests Fonctionnels Spécialisés

### 15. Test Voice Session

```bash
curl -X POST http://localhost:8000/api/voice/session \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64_encoded_audio",
    "language": "fr"
  }'
```

### 16. Test Email Sending

```bash
curl -X POST http://localhost:8000/api/mail/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body": "This is a test email from AgenticAI"
  }'
```

### 17. Test WebIntel Query

```bash
curl -X POST http://localhost:8000/api/webintel/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest AI developments",
    "max_results": 5
  }'
```

### 18. Test PM Risk Analysis

```bash
curl -X POST http://localhost:8000/api/pm/risks/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_data": {
      "name": "Project Alpha",
      "budget": 100000,
      "deadline": "2025-12-31"
    }
  }'
```

---

## 📊 Checklist de Validation

### Fonctionnalités de Base (Sans Docker)

- [ ] Login réussi avec admin@agenticai.dev
- [ ] Dashboard affiche les statistiques
- [ ] Liste des 19 agents visible
- [ ] Création d'un agent personnalisé
- [ ] Génération d'API key
- [ ] Formats de documents listés
- [ ] Cache stats accessible
- [ ] Monitoring insights accessible
- [ ] Création d'un nouveau compte utilisateur
- [ ] Documentation API accessible (/docs)

### Fonctionnalités Avancées (Avec Docker)

- [ ] Docker Compose lancé (PostgreSQL, Qdrant, Redis)
- [ ] Upload de document réussi
- [ ] Recherche sémantique fonctionne
- [ ] Ingestion RAG réussie
- [ ] Recherche RAG avec résultats pertinents
- [ ] Session vocale créée
- [ ] Email envoyé
- [ ] WebIntel query répond
- [ ] PM risk analysis fonctionne

---

## 🐛 Résolution de Problèmes

### Backend ne répond pas

```bash
# Vérifier le processus
lsof -ti:8000

# Redémarrer si nécessaire
kill $(lsof -ti:8000)
cd /Users/yahybouz/Desktop/Mes\ Scripts/AgenticAI-V4/backend
PYTHONPATH="$(pwd)" .venv/bin/python api/main.py
```

### Frontend ne charge pas

```bash
# Vérifier le processus
lsof -ti:3001

# Redémarrer si nécessaire
cd /Users/yahybouz/Desktop/Mes\ Scripts/AgenticAI-V4/frontend
npm run dev
```

### Erreur 401 Unauthorized

- Vérifier que le token est valide
- Se reconnecter pour obtenir un nouveau token
- Vérifier que le header Authorization est correct : `Bearer <token>`

### Erreur 404 Not Found

- Vérifier l'URL de l'endpoint
- Consulter la documentation : http://localhost:8000/docs
- Vérifier que la route existe dans `/openapi.json`

### Docker ne démarre pas

```bash
# Vérifier l'installation
docker --version

# Démarrer Docker Desktop manuellement
open -a Docker

# Attendre et vérifier
sleep 10
docker ps
```

---

## 📝 Rapport de Test

### Template de Rapport

```markdown
# Test Report - AgenticAI V4

**Date:** [Date]
**Testeur:** [Nom]

## Tests de Base (10/10)

- [✅/❌] Login
- [✅/❌] Dashboard
- [✅/❌] Liste Agents
- [✅/❌] Création Agent
- [✅/❌] API Key
- [✅/❌] Formats Documents
- [✅/❌] Cache Stats
- [✅/❌] Monitoring
- [✅/❌] Register
- [✅/❌] API Docs

## Tests Avancés (9/9)

- [✅/❌] Docker Lancé
- [✅/❌] Upload Document
- [✅/❌] Recherche Sémantique
- [✅/❌] Ingestion RAG
- [✅/❌] Recherche RAG
- [✅/❌] Voice Session
- [✅/❌] Email Send
- [✅/❌] WebIntel Query
- [✅/❌] PM Risk Analysis

## Commentaires

[Vos observations]

## Score Global

Tests réussis: [X] / 19 ([XX]%)
```

---

## 🚀 Prochaines Étapes Après Tests

1. **Optimisation** - Améliorer les performances
2. **Sécurité** - Audit de sécurité complet
3. **Scalabilité** - Tests de charge
4. **Documentation** - Compléter la documentation utilisateur
5. **Déploiement** - Préparer pour la production

---

**Bon testing ! 🎯**

*Pour toute question, consulter [FINAL_STATUS.md](FINAL_STATUS.md) ou la documentation API.*
