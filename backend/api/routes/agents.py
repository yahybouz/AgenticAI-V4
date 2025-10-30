from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from api.dependencies import get_agent_registry
from models import AgentDomain, AgentIO, AgentLifecycleStatus, AgentSkill, AgentSpec

router = APIRouter(prefix="/api/agents", tags=["Agents"])


class AgentCreateRequest(BaseModel):
    name: str
    domain: AgentDomain
    skills: list[AgentSkill]
    description: str
    input_schema: dict[str, str]
    output_schema: dict[str, str]


@router.get("/", response_model=list[AgentSpec])
async def list_agents(registry=Depends(get_agent_registry)):
    return registry.list()


@router.post("/", response_model=AgentSpec, status_code=201)
async def create_agent(payload: AgentCreateRequest, registry=Depends(get_agent_registry)):
    spec = AgentSpec(
        id=f"custom::{uuid.uuid4()}",
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
async def delete_agent(agent_id: str, registry=Depends(get_agent_registry)):
    agent = registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent introuvable")
    agent.status = AgentLifecycleStatus.RETIRED
    registry.register(agent)
    return {"status": "retired", "agent_id": agent_id}
