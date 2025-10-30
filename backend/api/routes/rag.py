from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.dependencies import get_master_orchestrator
from api.utils import extract_output
from models import AgentDomain, OrchestrationRequest

router = APIRouter(prefix="/api/rag", tags=["RAG"])


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 5


class RAGResult(BaseModel):
    text: str
    score: float
    source: str | None = None


class RAGResponse(BaseModel):
    results: List[RAGResult]


@router.post("/search", response_model=RAGResponse)
async def rag_search(payload: RAGQueryRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.RAG,
        objective="rag.searcher",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "rag.searcher")
    results = [RAGResult(**item) for item in data.get("results", [])]
    return RAGResponse(results=results)


class RAGIngestRequest(BaseModel):
    document_path: str
    metadata: dict[str, str] | None = None


@router.post("/ingest")
async def rag_ingest(payload: RAGIngestRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.RAG,
        objective="rag.indexer",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "rag.indexer")
    return {"trace_id": response.trace.trace_id, "status": data.get("status", response.status)}
