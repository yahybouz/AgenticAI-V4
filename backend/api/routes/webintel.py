from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.dependencies import get_master_orchestrator
from api.utils import extract_output
from models import AgentDomain, OrchestrationRequest

router = APIRouter(prefix="/api/webintel", tags=["Web Intelligence"])


class WebIntelQuery(BaseModel):
    topic: str
    sources_min: int = 3


@router.post("/query")
async def query_web(payload: WebIntelQuery, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.WEBINTEL,
        objective="web.factchecker",
        payload={"claims": [payload.topic], **payload.model_dump()},
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "web.factchecker")
    return {"trace_id": response.trace.trace_id, "status": response.status, "verdicts": data.get("verdicts", [])}


@router.get("/brief")
async def get_brief(topic: str):
    return {"topic": topic, "summary": "", "citations": []}
