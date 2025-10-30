from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.dependencies import get_master_orchestrator
from api.utils import extract_output
from models import AgentDomain, OrchestrationRequest

router = APIRouter(prefix="/api/mail", tags=["Mail"])


class MailSummarizeRequest(BaseModel):
    account_id: str
    thread_id: str


class MailSummary(BaseModel):
    summary: str
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


@router.post("/summarize", response_model=MailSummary)
async def summarize_mail(payload: MailSummarizeRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.MAIL,
        objective="mail.summarize",
        payload=payload.model_dump(),
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "mail.summarize")
    return MailSummary(
        summary=data.get("summary", ""),
        risks=data.get("risks", []),
        next_steps=data.get("next_steps", []),
    )


class MailReplyRequest(BaseModel):
    account_id: str
    thread_id: str
    instructions: str


class MailReplyDraft(BaseModel):
    draft: str
    requires_hitl: bool = True


@router.post("/reply", response_model=MailReplyDraft)
async def draft_reply(payload: MailReplyRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.MAIL,
        objective="mail.replydraft",
        payload=payload.model_dump(),
        human_in_the_loop=True,
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "mail.replydraft")
    return MailReplyDraft(draft=data.get("draft", ""), requires_hitl=True)


class MailSendRequest(BaseModel):
    draft_id: str
    approve: bool = False


@router.post("/send")
async def send_mail(payload: MailSendRequest, orchestrator=Depends(get_master_orchestrator)):
    request = OrchestrationRequest(
        domain=AgentDomain.MAIL,
        objective="mail.sender",
        payload=payload.model_dump(),
        human_in_the_loop=True,
    )
    response = await orchestrator.execute(request)
    data = extract_output(response, "mail.sender")
    return {"status": data.get("status", response.status), "trace_id": response.trace.trace_id}
