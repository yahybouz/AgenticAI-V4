# 🌟 NexusAI - Guide d'Installation

**The Connected Intelligence Platform**

---

## 🚀 Installation Ultra-Rapide

```bash
./install.sh
```

Le script installe automatiquement :
- ✅ Homebrew (si nécessaire)
- ✅ Python 3.11+
- ✅ Node.js + npm
- ✅ Ollama + modèles LLM (qwen2.5:14b, nomic-embed-text)
- ✅ Backend Python (FastAPI + dépendances)
- ✅ Frontend React (npm packages)
- ✅ Base de données SQLite
- ✅ Scripts de démarrage

**Durée:** 15-30 minutes (selon connexion internet)

---

## 📋 Prérequis

- **macOS** (testé sur macOS 10.15+)
- **16 GB RAM** minimum (32 GB recommandé)
- **50 GB** d'espace disque libre
- **Connexion internet** (pour télécharger les modèles)

---

## 📖 Installation Étape par Étape

### Étape 1 : Cloner le Projet

```bash
git clone https://github.com/yahybouz/AgenticAI-V4.git
cd AgenticAI-V4
```

### Étape 2 : Lancer l'Installation

```bash
./install.sh
```

Le script va :
1. Vérifier votre système
2. Installer les dépendances
3. Télécharger les modèles Ollama (~9 GB)
4. Configurer backend et frontend
5. Créer les scripts de démarrage

### Étape 3 : Démarrer NexusAI

```bash
./start.sh
```

### Étape 4 : Ouvrir dans le Navigateur

```bash
open http://localhost:3001
```

**Ou visitez :** http://localhost:3001

**Identifiants :**
```
Email:    admin@agenticai.dev
Password: admin123
```

---

## 🎯 Utilisation Quotidienne

### Démarrer NexusAI

```bash
./start.sh
```

Cela démarre :
- Backend API sur http://localhost:8000
- Frontend Web sur http://localhost:3001
- Documentation API sur http://localhost:8000/docs

### Arrêter NexusAI

**Méthode 1 :** Dans le terminal où `start.sh` tourne
```
Ctrl + C
```

**Méthode 2 :** Script d'arrêt
```bash
./stop.sh
```

---

## 🛠️ Installation Manuelle (Avancé)

Si vous préférez installer manuellement :

### Backend

```bash
cd backend

# Créer environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Démarrer
PYTHONPATH="$(pwd)" python api/main.py
```

### Frontend

```bash
cd frontend

# Installer dépendances
npm install

# Démarrer
npm run dev
```

### Ollama

```bash
# Installer Ollama
brew install ollama

# Démarrer le service
brew services start ollama

# Télécharger les modèles
ollama pull qwen2.5:14b
ollama pull nomic-embed-text
```

---

## 🐳 Installation avec Docker (Optionnel)

Pour utiliser PostgreSQL, Qdrant, et Redis :

### 1. Installer Docker Desktop

```bash
brew install --cask docker
```

Puis lancez Docker Desktop.

### 2. Démarrer les Services

```bash
docker compose up -d
```

### 3. Vérifier les Services

```bash
docker compose ps
```

### 4. Arrêter les Services

```bash
docker compose down
```

---

## 🧪 Vérifier l'Installation

### Test Backend

```bash
curl http://localhost:8000/health
```

**Résultat attendu :**
```json
{"status":"degraded","timestamp":"..."}
```

### Test Frontend

```bash
curl -I http://localhost:3001
```

**Résultat attendu :**
```
HTTP/1.1 200 OK
```

### Test API

```bash
curl http://localhost:8000/info | python3 -m json.tool
```

**Résultat attendu :**
```json
{
  "version": "4.0.0",
  "agents": {...},
  "orchestrator": "MasterOrchestrator"
}
```

---

## 🔧 Dépannage

### Problème : Port déjà utilisé

**Erreur :** `Address already in use`

**Solution :**
```bash
# Trouver et tuer le processus
lsof -ti:8000 | xargs kill -9
lsof -ti:3001 | xargs kill -9
```

### Problème : Modèle Ollama manquant

**Erreur :** `model not found`

**Solution :**
```bash
ollama pull qwen2.5:14b
```

### Problème : Dépendances Python manquantes

**Solution :**
```bash
cd backend
.venv/bin/pip install -r requirements.txt
```

### Problème : Dépendances npm manquantes

**Solution :**
```bash
cd frontend
npm install
```

### Problème : Base de données corrompue

**Solution :**
```bash
# Supprimer et recréer la DB
rm backend/agenticai.db
./start.sh  # La DB sera recréée automatiquement
```

---

## 📚 Structure du Projet

```
NexusAI/
├── install.sh              # Script d'installation
├── start.sh               # Démarrage rapide
├── stop.sh                # Arrêt propre
├── backend/               # API FastAPI
│   ├── .venv/            # Environnement virtuel Python
│   ├── api/              # Routes API
│   ├── models/           # Modèles de données
│   ├── services/         # Logique métier
│   └── agenticai.db      # Base SQLite
├── frontend/              # Application React
│   ├── src/              # Code source TypeScript
│   └── node_modules/     # Dépendances npm
├── docker-compose.yml     # Services Docker (optionnel)
└── README.md             # Documentation principale
```

---

## 🔐 Configuration

### Backend (.env)

```bash
# backend/.env
DATABASE_URL=sqlite+aiosqlite:///./agenticai.db
JWT_SECRET_KEY=your-secret-key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:14b
```

### Frontend (.env)

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🎓 Prochaines Étapes

Après l'installation :

1. ✅ **Tester les 13 pages**
   - Dashboard, Agents, Documents, Chat
   - Voice, WebIntel, Coach
   - Mail, PM, Docs
   - Monitoring

2. ✅ **Explorer l'API**
   - http://localhost:8000/docs
   - Tester les 40 endpoints

3. ✅ **Créer vos agents**
   - Page Agents > "Créer un agent"
   - Personnaliser les compétences

4. ✅ **Uploader des documents**
   - Page Documents > Drag & Drop
   - Tester la recherche sémantique

---

## 🆘 Support

### Documentation
- **README.md** - Vue d'ensemble
- **FINAL_STATUS.md** - État complet du système
- **API Docs** - http://localhost:8000/docs

### Logs
```bash
# Logs backend (terminal où start.sh tourne)
# Logs frontend (même terminal)
# Logs Docker
docker compose logs -f
```

### GitHub
https://github.com/yahybouz/AgenticAI-V4

---

## ✅ Checklist d'Installation

- [ ] Homebrew installé
- [ ] Python 3.11+ installé
- [ ] Node.js installé
- [ ] Ollama installé
- [ ] Modèle qwen2.5:14b téléchargé
- [ ] Backend démarre sans erreur
- [ ] Frontend accessible sur :3001
- [ ] Login fonctionne
- [ ] Dashboard affiche les graphiques

---

**🌟 Félicitations ! NexusAI est installé ! 🌟**

**Commencez maintenant :**
```bash
./start.sh
```

Puis ouvrez http://localhost:3001
