from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencies import get_master_orchestrator
from models import OrchestratorPolicy
from orchestrators.trace_store import trace_store

router = APIRouter(prefix="/api/orchestrator", tags=["Orchestrator"])


class PolicyUpdateRequest(BaseModel):
    policy: OrchestratorPolicy


@router.post("/policy")
async def update_policy(payload: PolicyUpdateRequest, orchestrator=Depends(get_master_orchestrator)):
    orchestrator.policy = payload.policy
    return {"status": "updated"}


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str):
    trace = trace_store.get(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace introuvable")
    return trace
