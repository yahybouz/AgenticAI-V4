from __future__ import annotations

from agents import AgentRegistry
from models import AgentDomain, OrchestrationRequest, OrchestratorPolicy
from services import AgentExecutor, DatabaseService, MessagingService, OllamaService, VectorStoreService

from .base import BaseOrchestrator, default_policy


class DomainOrchestrator(BaseOrchestrator):
    def __init__(
        self,
        domain: AgentDomain,
        registry: AgentRegistry,
        *,
        policy: OrchestratorPolicy | None = None,
        executor: AgentExecutor,
        ollama: OllamaService,
        vector_store: VectorStoreService,
        database: DatabaseService,
        messaging: MessagingService,
    ) -> None:
        super().__init__(
            name=f"orchestrator::{domain.value}",
            domain=domain,
            policy=policy or default_policy(domain),
            registry=registry,
            executor=executor,
            ollama=ollama,
            vector_store=vector_store,
            database=database,
            messaging=messaging,
        )

    async def plan(self, request: OrchestrationRequest):  # type: ignore[override]
        plan = await super().plan(request)
        plan["domain"] = self.domain.value if self.domain else "general"
        return plan
