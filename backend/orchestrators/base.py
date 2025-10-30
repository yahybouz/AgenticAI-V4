from __future__ import annotations

import logging
import uuid
from typing import Dict, List

from agents import AgentRegistry
from models import (
    AgentDomain,
    ExecutionTrace,
    GuardedAction,
    OrchestrationRequest,
    OrchestrationResponse,
    OrchestratorPolicy,
    OrchestratorScope,
)
from services import AgentExecutor, DatabaseService, MessagingService, OllamaService, VectorStoreService

from .trace_store import trace_store

logger = logging.getLogger(__name__)


class BaseOrchestrator:
    """Shared logic for all orchestrators."""

    def __init__(
        self,
        name: str,
        domain: AgentDomain | None,
        policy: OrchestratorPolicy,
        registry: AgentRegistry,
        *,
        executor: AgentExecutor,
        ollama: OllamaService,
        vector_store: VectorStoreService,
        database: DatabaseService,
        messaging: MessagingService,
    ) -> None:
        self.name = name
        self.domain = domain
        self.policy = policy
        self.registry = registry
        self.executor = executor
        self.ollama = ollama
        self.vector_store = vector_store
        self.database = database
        self.messaging = messaging

    async def plan(self, request: OrchestrationRequest) -> Dict[str, object]:
        steps: List[str]
        target_agent = self.registry.get(request.objective)
        if target_agent:
            steps = [target_agent.id]
        elif request.domain:
            steps = [agent.id for agent in self.registry.list_by_domain(request.domain)]
        else:
            steps = [agent.id for agent in self.registry.list()]

        plan = {
            "steps": steps[: self.policy.max_agents],
            "objective": request.objective,
        }
        logger.debug("[Orchestrator] plan", extra={"name": self.name, "plan": plan})
        return plan

    async def execute(self, request: OrchestrationRequest) -> OrchestrationResponse:
        plan = await self.plan(request)
        trace = ExecutionTrace(
            trace_id=str(uuid.uuid4()),
            orchestrator=self.name,
            inputs=request.model_dump(),
            plan=plan,
            result={"status": "pending", "executions": []},
        )

        executions = []
        status = "accepted"
        for agent_id in plan["steps"]:
            try:
                exec_result = await self.executor.execute(agent_id, request.payload)
                executions.append(exec_result.model_dump())
            except Exception as exc:  # pragma: no cover
                logger.error("[Orchestrator] agent failure", extra={"agent": agent_id, "error": str(exc)})
                executions.append({"agent_id": agent_id, "success": False, "error": str(exc)})
                status = "error"
                break

        trace.result = {"status": status, "executions": executions}
        trace_store.add(trace)
        await self.messaging.publish("orchestrator.trace", trace.model_dump())
        message = "Plan exécuté" if status == "accepted" else "Plan interrompu"
        logger.info("[Orchestrator] execute", extra={"name": self.name, "objective": request.objective, "status": status})
        return OrchestrationResponse(trace=trace, status=status, message=message)


def default_policy(domain: AgentDomain | None = None) -> OrchestratorPolicy:
    require_hitl = []
    if domain in {AgentDomain.MAIL, AgentDomain.WEBINTEL}:
        require_hitl = [
            GuardedAction.SEND_EMAIL_EXTERNAL,
            GuardedAction.CREATE_SUB_ORCHESTRATOR,
        ]
    return OrchestratorPolicy(
        id=f"policy::{domain or 'master'}",
        scope=OrchestratorScope.DOMAIN if domain else OrchestratorScope.MASTER,
        domain=domain,
        guarded_actions=require_hitl,
        require_human_approval=require_hitl,
    )
