from __future__ import annotations

from functools import lru_cache

from agents import AgentRegistry, get_registry
from orchestrators import MasterOrchestrator
from services import (
    AgentExecutor,
    DatabaseService,
    MessagingService,
    MonitoringService,
    OllamaService,
    VectorStoreService,
)


@lru_cache
def get_agent_registry() -> AgentRegistry:
    return get_registry()


@lru_cache
def get_ollama_service() -> OllamaService:
    return OllamaService()


@lru_cache
def get_vector_store() -> VectorStoreService:
    return VectorStoreService()


@lru_cache
def get_database_service() -> DatabaseService:
    return DatabaseService()


@lru_cache
def get_messaging_service() -> MessagingService:
    return MessagingService()


@lru_cache
def get_monitoring_service() -> MonitoringService:
    return MonitoringService()


@lru_cache
def get_agent_executor() -> AgentExecutor:
    return AgentExecutor(
        registry=get_agent_registry(),
        database=get_database_service(),
    )


@lru_cache
def get_master_orchestrator() -> MasterOrchestrator:
    return MasterOrchestrator(
        registry=get_agent_registry(),
        executor=get_agent_executor(),
        ollama=get_ollama_service(),
        vector_store=get_vector_store(),
        database=get_database_service(),
        messaging=get_messaging_service(),
    )
