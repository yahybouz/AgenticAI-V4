from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.dependencies import get_database_service, get_master_orchestrator
from api.utils import extract_output
from models import AgentDomain, OrchestrationRequest

router = APIRouter(prefix="/api/coach", tags=["Coach Santé"])


class HealthLog(BaseModel):
    user_id: str
    metric: str
    value: float
    note: str | None = None


@router.post("/log")
async def log_metric(payload: HealthLog, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.COACH,
        objective="coach.logingest",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "coach.logingest")
    return {"status": response.status, "trace_id": response.trace.trace_id, "stored": data.get("stored", False)}


class CoachReport(BaseModel):
    user_id: str
    period: str = "week"


@router.get("/report")
async def get_report(user_id: str, period: str = "week", db=Depends(get_database_service)):
    logs = await db.fetch_health_logs(user_id)
    return {"user_id": user_id, "period": period, "logs": logs}
