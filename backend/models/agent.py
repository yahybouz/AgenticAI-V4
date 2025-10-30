"""Data models describing agents and capabilities."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AgentDomain(str, Enum):
    VOICE = "voice"
    MAIL = "mail"
    RAG = "rag"
    CHAT = "chat"
    COACH = "coach"
    DOCS = "docs"
    SCREEN = "screen"
    WEBINTEL = "webintel"
    PM = "pm"


class AgentLifecycleStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    RETIRED = "retired"


class AgentSkill(str, Enum):
    SPEECH_TO_TEXT = "speech_to_text"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    RAG_INDEX = "rag_index"
    RAG_SEARCH = "rag_search"
    QA = "qa"
    OCR = "ocr"
    FACT_CHECK = "fact_check"
    PM_REPORTING = "pm_reporting"
    HEALTH_ANALYTICS = "health_analytics"
    DOCUMENT_FORMATTING = "document_formatting"


class AgentIO(BaseModel):
    """Describes the IO contract of an agent."""

    input_schema: Dict[str, str]
    output_schema: Dict[str, str]


class AgentSpec(BaseModel):
    id: str
    name: str
    domain: AgentDomain
    skills: List[AgentSkill]
    description: str
    io: AgentIO
    owner: str = "system"
    policy_id: Optional[str] = None
    status: AgentLifecycleStatus = AgentLifecycleStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentExecutionRequest(BaseModel):
    agent_id: str
    payload: Dict[str, object] | None = None
    input: Dict[str, object] | None = None  # Alias pour payload
    priority: Literal["low", "normal", "high"] = "normal"

    def model_post_init(self, __context):
        """Support both 'payload' and 'input' field names"""
        if self.input is not None and self.payload is None:
            self.payload = self.input
        elif self.payload is not None and self.input is None:
            self.input = self.payload
        elif self.payload is None and self.input is None:
            self.payload = {}
            self.input = {}


class AgentExecutionResult(BaseModel):
    agent_id: str = Field(default="unknown")
    success: bool
    output: Dict[str, object]
    latency_ms: int = Field(default=0)
    trace_id: str = Field(default="")
    error: Optional[str] = None
    citations: List[Dict[str, str]] = Field(default_factory=list)

