from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.dependencies import get_master_orchestrator
from api.utils import extract_output
from models import AgentDomain, OrchestrationRequest

router = APIRouter(prefix="/api/pm", tags=["PM IT"])


class RiskAnalyzeRequest(BaseModel):
    project_id: str
    sources: list[str]


@router.post("/risks/analyze")
async def analyze_risks(payload: RiskAnalyzeRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.PM,
        objective="pm.riskminer",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "pm.riskminer")
    return {"trace_id": response.trace.trace_id, "status": response.status, "risks": data.get("risks", [])}


class CODIRReportRequest(BaseModel):
    project_id: str
    sprint: str


@router.get("/report/codir")
async def codir_report(project_id: str, sprint: str):
    return {"project_id": project_id, "sprint": sprint, "sections": []}
