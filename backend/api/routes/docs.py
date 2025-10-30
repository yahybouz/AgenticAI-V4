from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.dependencies import get_master_orchestrator
from api.utils import extract_output
from models import AgentDomain, OrchestrationRequest

router = APIRouter(prefix="/api/docs", tags=["Docs & CR"])


class CRBuildRequest(BaseModel):
    meeting_id: str
    sections: list[str] = Field(default_factory=lambda: ["Decisions", "Actions", "Risques"])


@router.post("/cr/build")
async def build_cr(payload: CRBuildRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.DOCS,
        objective="cr.builder",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "cr.builder")
    return {"status": response.status, "trace_id": response.trace.trace_id, "document_id": data.get("document_id")}


class CompileRequest(BaseModel):
    doc_id: str
    format: str = "pdf"


@router.post("/compile")
async def compile_doc(payload: CompileRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.DOCS,
        objective="docs.formatter",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "docs.formatter")
    return {"artifact_path": data.get("path", f"/tmp/{payload.doc_id}.{payload.format}"), "trace_id": response.trace.trace_id}
