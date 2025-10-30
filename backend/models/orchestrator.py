"""Policies and orchestrator data structures."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal

from pydantic import BaseModel, Field

from .agent import AgentDomain


class GuardedAction(str, Enum):
    SEND_EMAIL_EXTERNAL = "send_email_external"
    SHARE_FILE = "share_file"
    CHANGE_POLICIES = "change_policies"
    CREATE_SUB_ORCHESTRATOR = "create_sub_orchestrator"


class OrchestratorScope(str, Enum):
    MASTER = "master"
    DOMAIN = "domain"


class PolicyRule(BaseModel):
    name: str
    description: str
    threshold: float | int | None = None
    action: str


class OrchestratorPolicy(BaseModel):
    id: str
    scope: OrchestratorScope
    domain: AgentDomain | None = None
    max_agents: int = 12
    creation_rate_limit_per_min: int = 3
    guarded_actions: List[GuardedAction] = Field(default_factory=list)
    require_human_approval: List[GuardedAction] = Field(default_factory=list)
    rules: List[PolicyRule] = Field(default_factory=list)


class ExecutionTrace(BaseModel):
    trace_id: str
    orchestrator: str
    inputs: Dict[str, object]
    plan: Dict[str, object]
    result: Dict[str, object]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrchestrationRequest(BaseModel):
    domain: AgentDomain
    objective: str
    payload: Dict[str, object]
    priority: Literal["low", "normal", "high"] = "normal"
    human_in_the_loop: bool = False


class OrchestrationResponse(BaseModel):
    trace: ExecutionTrace
    status: Literal["accepted", "rejected", "pending"]
    message: str

