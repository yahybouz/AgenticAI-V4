"""
AgenticAI V4 - FastAPI Backend
Point d'entrée principal de l'API
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from api import dependencies
from api.routes import (
    agents,
    auth,
    coach,
    docs,
    documents,
    mail,
    monitoring,
    orchestrator,
    pm,
    rag,
    voice,
    webintel,
)
from agents import seed_default_agents
from config import get_settings
from models import AgentDomain, OrchestrationRequest

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 AgenticAI V4 - Démarrage")

    # Initialize database and create default admin
    user_service = dependencies.get_user_service()
    await user_service.init_db()
    logger.info("✅ Base de données initialisée")

    # Initialize agents and orchestrator
    seed_default_agents()
    dependencies.get_master_orchestrator()
    logger.info("✅ Système prêt")

    yield
    logger.info("🛑 AgenticAI V4 - Arrêt")


app = FastAPI(
    title=settings.project_name,
    description="Assistant IA Multi-Agents Local via Ollama",
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(auth.router)
app.include_router(voice.router)
app.include_router(mail.router)
app.include_router(rag.router)
app.include_router(documents.router)
app.include_router(coach.router)
app.include_router(docs.router)
app.include_router(webintel.router)
app.include_router(pm.router)
app.include_router(agents.router)
app.include_router(orchestrator.router)
app.include_router(monitoring.router)


@app.get("/")
async def root():
    return {
        "name": settings.project_name,
        "version": settings.api_version,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "up",
            "ollama": "pending",
            "postgres": "pending",
            "qdrant": "pending",
            "redis": "pending",
        },
    }


@app.get("/info")
async def system_info():
    registry = dependencies.get_agent_registry()
    orchestrator = dependencies.get_master_orchestrator()
    return {
        "version": settings.api_version,
        "agents": {
            "total": len(registry.list()),
            "domains": sorted({agent.domain.value for agent in registry.list()}),
        },
        "orchestrator": orchestrator.name,
    }


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    orchestrator = dependencies.get_master_orchestrator()
    try:
        while True:
            data = await websocket.receive_json()
            request = OrchestrationRequest(
                domain=AgentDomain.CHAT,
                objective="chat.agentcreator",
                payload=data,
            )
            response = await orchestrator.execute(request)
            await websocket.send_json(
                {
                    "trace_id": response.trace.trace_id,
                    "status": response.status,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket chat déconnecté")


@app.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    await websocket.accept()
    orchestrator = dependencies.get_master_orchestrator()
    try:
        while True:
            await websocket.receive_bytes()
            request = OrchestrationRequest(
                domain=AgentDomain.VOICE,
                objective="voice.transcribe",
                payload={"chunk": "received"},
            )
            response = await orchestrator.execute(request)
            await websocket.send_json(
                {
                    "trace_id": response.trace.trace_id,
                    "transcript": "",
                    "translation": "",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket voice déconnecté")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"❌ Exception non gérée: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Démarrage serveur FastAPI...")
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
