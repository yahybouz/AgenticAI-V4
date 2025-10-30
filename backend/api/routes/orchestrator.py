from __future__ import annotations

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.dependencies import get_master_orchestrator, get_current_active_user
from models import OrchestratorPolicy
from models.user import User
from orchestrators.trace_store import trace_store

router = APIRouter(prefix="/api/orchestrator", tags=["Orchestrator"])


class PolicyUpdateRequest(BaseModel):
    policy: OrchestratorPolicy


@router.post("/policy")
async def update_policy(
    current_user: Annotated[User, Depends(get_current_active_user)],
    payload: PolicyUpdateRequest,
    orchestrator=Depends(get_master_orchestrator)
):
    """
    Met à jour les politiques d'orchestration.

    Requiert authentification (réservé aux admins en production).
    """
    # TODO: Vérifier que l'utilisateur est admin
    # if current_user.role != UserRole.ADMIN:
    #     raise HTTPException(status_code=403, detail="Admin uniquement")

    orchestrator.policy = payload.policy
    return {"status": "updated", "updated_by": current_user.username}


@router.get("/trace/{trace_id}")
async def get_trace(
    current_user: Annotated[User, Depends(get_current_active_user)],
    trace_id: str
):
    """
    Récupère une trace d'exécution d'orchestration.

    Requiert authentification.
    """
    trace = trace_store.get(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace introuvable")

    # TODO: Vérifier que la trace appartient à l'utilisateur
    # if trace.get("user_id") != current_user.id and current_user.role != UserRole.ADMIN:
    #     raise HTTPException(status_code=403, detail="Accès refusé")

    return trace
