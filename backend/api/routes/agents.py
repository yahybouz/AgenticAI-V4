from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import get_agent_registry, get_current_active_user
from models import AgentDomain, AgentIO, AgentLifecycleStatus, AgentSkill, AgentSpec
from models.user import User

router = APIRouter(prefix="/api/agents", tags=["Agents"])


class AgentCreateRequest(BaseModel):
    name: str
    domain: AgentDomain
    skills: list[AgentSkill]
    description: str
    input_schema: dict[str, str]
    output_schema: dict[str, str]


@router.get("/", response_model=list[AgentSpec])
async def list_agents(
    current_user: Annotated[User, Depends(get_current_active_user)],
    registry=Depends(get_agent_registry)
):
    """
    Liste tous les agents disponibles.

    Requiert authentification.
    TODO: Filtrer par user_id pour agents personnalisés.
    """
    # TODO: Filtrer par current_user.id pour agents personnalisés
    return registry.list()


@router.post("/", response_model=AgentSpec, status_code=201)
async def create_agent(
    current_user: Annotated[User, Depends(get_current_active_user)],
    payload: AgentCreateRequest,
    registry=Depends(get_agent_registry)
):
    """
    Crée un agent personnalisé.

    Requiert authentification. L'agent sera associé à l'utilisateur.
    """
    # Vérifier les quotas
    # TODO: Compter les agents de l'utilisateur et vérifier current_user.max_agents

    spec = AgentSpec(
        id=f"custom::{current_user.id}::{uuid.uuid4()}",  # ID avec user_id
        name=payload.name,
        domain=payload.domain,
        skills=payload.skills,
        description=payload.description,
        io=AgentIO(input_schema=payload.input_schema, output_schema=payload.output_schema),
        status=AgentLifecycleStatus.DRAFT,
    )
    registry.register(spec)
    return spec


@router.delete("/{agent_id}")
async def delete_agent(
    current_user: Annotated[User, Depends(get_current_active_user)],
    agent_id: str,
    registry=Depends(get_agent_registry)
):
    """
    Supprime (retire) un agent.

    Requiert authentification. Seul le propriétaire peut supprimer son agent.
    """
    agent = registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent introuvable")

    # TODO: Vérifier que l'agent appartient à l'utilisateur
    # if not agent_id.startswith(f"custom::{current_user.id}") and current_user.role != UserRole.ADMIN:
    #     raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres agents")

    agent.status = AgentLifecycleStatus.RETIRED
    registry.register(agent)
    return {"status": "retired", "agent_id": agent_id, "deleted_by": current_user.username}
