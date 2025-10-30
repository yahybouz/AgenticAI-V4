#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
VENV_DIR="$ROOT_DIR/backend/.venv"
REQUIREMENTS_FILE="$ROOT_DIR/backend/requirements-dev.txt"
BACKEND_LOG="$LOG_DIR/backend.log"
BACKEND_PID_FILE="$ROOT_DIR/backend/.uvicorn.pid"
FRONTEND_PID_FILE="$ROOT_DIR/frontend/.next.pid"

mkdir -p "$LOG_DIR"

info() { printf "\033[1;34m[INFO]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[WARN]\033[0m %s\n" "$*"; }
error() { printf "\033[1;31m[ERR ]\033[0m %s\n" "$*"; }

ensure_env_file() {
  if [ ! -f "$ROOT_DIR/.env" ]; then
    if [ -f "$ROOT_DIR/.env.example" ]; then
      warn ".env introuvable, copie depuis .env.example"
      cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
    else
      error ".env.example absent, impossible de continuer"
      exit 1
    fi
  fi
}

require_brew() {
  if ! command -v brew >/dev/null 2>&1; then
    error "Homebrew est nécessaire pour installer automatiquement Docker/Colima."
    echo "Installe-le via :"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
  fi
}

install_docker_stack() {
  if command -v docker >/dev/null 2>&1; then
    info "Docker déjà installé"
  else
    require_brew
    info "Installation de Docker Desktop (brew install --cask docker)"
    brew install --cask docker || warn "Échec installation Docker Desktop. Lancez l'application manuellement après installation."
  fi

  if command -v colima >/dev/null 2>&1; then
    info "Colima déjà installé"
  else
    require_brew
    info "Installation de Colima (runtime Docker léger)"
    brew install colima || warn "Échec installation Colima"
  fi

  if [ -d "/Applications/Docker.app" ]; then
    info "Ouverture de Docker Desktop"
    open -ga Docker || warn "Impossible de lancer Docker.app automatiquement"
  fi

  if ! docker info >/dev/null 2>&1; then
    if command -v colima >/dev/null 2>&1; then
      info "Démarrage de Colima"
      colima start || warn "Impossible de démarrer Colima"
    fi
  fi

  if ! docker info >/dev/null 2>&1; then
    error "Docker/Colima toujours indisponible après tentative d'installation."
    exit 1
  fi
}

ensure_docker_compose() {
  if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
  elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=(docker-compose)
  else
    require_brew
    info "Installation docker-compose"
    brew install docker-compose
    COMPOSE_CMD=(docker-compose)
  fi
}

ensure_python_env() {
  if [ ! -d "$VENV_DIR" ]; then
    info "Création de l'environnement virtuel backend (.venv)"
    python3 -m venv "$VENV_DIR"
  fi
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  info "Mise à jour de pip"
  pip install --upgrade pip >/dev/null
  if [ -f "$REQUIREMENTS_FILE" ]; then
    info "Installation des dépendances backend"
    pip install -r "$REQUIREMENTS_FILE" >/dev/null
  else
    warn "requirements-dev.txt absent, installation minimale"
    pip install fastapi uvicorn[standard] >/dev/null
  fi
}

install_frontend_tooling() {
  if [ -f "$ROOT_DIR/frontend/package.json" ]; then
    if command -v pnpm >/dev/null 2>&1; then
      info "pnpm déjà installé"
    else
      if command -v npm >/dev/null 2>&1; then
        warn "pnpm absent, utilisation de npm"
      else
        require_brew
        info "Installation de npm (Node.js)"
        brew install node || warn "Échec installation Node.js"
      fi
    fi
  fi
}

start_infra() {
  ensure_docker_compose
  info "Démarrage de l'infrastructure Docker (ollama, postgres, qdrant, redis, minio, observabilité)"
  "${COMPOSE_CMD[@]}" -f "$ROOT_DIR/docker-compose.yml" up -d ollama postgres qdrant redis minio jaeger prometheus grafana
}

run_migrations_stub() {
  if [ -f "$ROOT_DIR/backend/scripts/migrate.py" ]; then
    info "Exécution des migrations backend"
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
    python "$ROOT_DIR/backend/scripts/migrate.py"
  else
    warn "Aucune migration automatique définie"
  fi
}

start_backend() {
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"
  info "Lancement du backend FastAPI (logs : $BACKEND_LOG)"
  if [ -f "$BACKEND_PID_FILE" ] && kill -0 "$(cat "$BACKEND_PID_FILE")" >/dev/null 2>&1; then
    warn "Backend déjà en cours d'exécution (PID $(cat "$BACKEND_PID_FILE"))"
    return
  fi
  nohup uvicorn backend.api.main:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}" --reload \
    >>"$BACKEND_LOG" 2>&1 &
  echo $! > "$BACKEND_PID_FILE"
  info "Backend démarré (PID $(cat "$BACKEND_PID_FILE"))"
}

start_frontend() {
  if [ -f "$ROOT_DIR/frontend/package.json" ]; then
    install_frontend_tooling
    if [ -f "$FRONTEND_PID_FILE" ] && kill -0 "$(cat "$FRONTEND_PID_FILE")" >/dev/null 2>&1; then
      warn "Frontend déjà en cours d'exécution"
      return
    fi
    info "Installation des dépendances frontend"
    pushd "$ROOT_DIR/frontend" >/dev/null
    if command -v pnpm >/dev/null 2>&1; then
      pnpm install
      pnpm dev >>"$LOG_DIR/frontend.log" 2>&1 &
    else
      npm install
      npm run dev >>"$LOG_DIR/frontend.log" 2>&1 &
    fi
    echo $! > "$FRONTEND_PID_FILE"
    popd >/dev/null
    info "Frontend Next.js démarré"
  else
    warn "Frontend non initialisé (frontend/package.json absent)"
  fi
}

run_tests() {
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  info "Exécution de la suite Pytest"
  pytest || warn "Tests en échec"
}

print_summary() {
  cat <<EOT

========================================
Services lancés :
- Docker compose : ollama, postgres, qdrant, redis, minio, jaeger, prometheus, grafana
- Backend FastAPI : http://localhost:${API_PORT:-8000} (logs -> $BACKEND_LOG)
- Frontend : http://localhost:3000 (si présent)
- Grafana : http://localhost:3001 (admin/admin)
- Prometheus : http://localhost:9090
- Jaeger UI : http://localhost:16686
========================================
EOT
}

main() {
  ensure_env_file
  install_docker_stack
  ensure_python_env
  start_infra
  run_migrations_stub
  start_backend
  start_frontend
  if [[ "${RUN_TESTS:-false}" == "true" ]]; then
    run_tests
  fi
  print_summary
}

main "$@"
