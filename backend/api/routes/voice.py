from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.dependencies import get_master_orchestrator
from models import AgentDomain, OrchestrationRequest

router = APIRouter(prefix="/api/voice", tags=["Voice"])


class VoiceSessionRequest(BaseModel):
    meeting_id: str
    language: str = "fr"
    translation_language: str | None = None


class VoiceSessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: datetime


class VoiceBookmark(BaseModel):
    session_id: str
    label: str = Field(description="Action ou Décision")
    timestamp: float


@router.post("/session", response_model=VoiceSessionResponse)
async def start_session(payload: VoiceSessionRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.VOICE,
        objective="voice.capture",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    return VoiceSessionResponse(
        session_id=response.trace.trace_id,
        status=response.status,
        created_at=response.trace.created_at,
    )


class LiveTranscript(BaseModel):
    transcript: List[str]
    translation: List[str]


@router.get("/live", response_model=LiveTranscript)
async def live_feed(meeting_id: str):
    return LiveTranscript(transcript=[], translation=[])


@router.post("/bookmark")
async def create_bookmark(payload: VoiceBookmark, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.VOICE,
        objective="voice.qa",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    return {"bookmark_id": response.trace.trace_id, "status": response.status}
