from __future__ import annotations

from typing import Dict

from agents import AgentRegistry
from models import AgentDomain, OrchestrationRequest, OrchestrationResponse
from services import AgentExecutor, DatabaseService, MessagingService, OllamaService, VectorStoreService

from .base import BaseOrchestrator, default_policy
from .domain import DomainOrchestrator


class MasterOrchestrator(BaseOrchestrator):
    def __init__(
        self,
        registry: AgentRegistry,
        *,
        executor: AgentExecutor,
        ollama: OllamaService,
        vector_store: VectorStoreService,
        database: DatabaseService,
        messaging: MessagingService,
    ) -> None:
        super().__init__(
            name="orchestrator::master",
            domain=None,
            policy=default_policy(None),
            registry=registry,
            executor=executor,
            ollama=ollama,
            vector_store=vector_store,
            database=database,
            messaging=messaging,
        )
        self.sub_orchestrators: Dict[AgentDomain, DomainOrchestrator] = {}
        self.executor = executor

    def get_sub(self, domain: AgentDomain) -> DomainOrchestrator:
        if domain not in self.sub_orchestrators:
            self.sub_orchestrators[domain] = DomainOrchestrator(
                domain,
                registry=self.registry,
                executor=self.executor,
                ollama=self.ollama,
                vector_store=self.vector_store,
                database=self.database,
                messaging=self.messaging,
            )
        return self.sub_orchestrators[domain]

    async def execute(self, request: OrchestrationRequest) -> OrchestrationResponse:  # type: ignore[override]
        sub = self.get_sub(request.domain)
        return await sub.execute(request)
