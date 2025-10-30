"""Simple in-memory registry seeded from cahier des charges."""
from __future__ import annotations

from typing import Dict, Iterable, List

from pydantic import BaseModel

from models import (
    AgentDomain,
    AgentIO,
    AgentSkill,
    AgentSpec,
)


class AgentRegistry(BaseModel):
    """Stores agent specifications locally."""

    agents: Dict[str, AgentSpec] = {}

    def register(self, spec: AgentSpec) -> None:
        self.agents[spec.id] = spec

    def get(self, agent_id: str) -> AgentSpec | None:
        return self.agents.get(agent_id)

    def list(self) -> List[AgentSpec]:
        return list(self.agents.values())

    def list_by_domain(self, domain: AgentDomain) -> List[AgentSpec]:
        return [agent for agent in self.agents.values() if agent.domain == domain]


_registry = AgentRegistry()


def seed_default_agents() -> None:
    """Populate registry with default agents per cahier des charges."""

    default_agents: Iterable[AgentSpec] = [
        AgentSpec(
            id="voice.capture",
            name="Voice Capture",
            domain=AgentDomain.VOICE,
            skills=[AgentSkill.SPEECH_TO_TEXT],
            description="Capture audio packets via WebRTC avec VAD",
            io=AgentIO(
                input_schema={"audio_stream": "bytes"},
                output_schema={"chunk_path": "str", "duration": "float"},
            ),
        ),
        AgentSpec(
            id="voice.transcribe",
            name="Voice Transcribe",
            domain=AgentDomain.VOICE,
            skills=[AgentSkill.SPEECH_TO_TEXT],
            description="Transcrit en local via whisper",
            io=AgentIO(input_schema={"chunk_path": "str"}, output_schema={"text": "str"}),
        ),
        AgentSpec(
            id="voice.translate",
            name="Voice Translate",
            domain=AgentDomain.VOICE,
            skills=[AgentSkill.TRANSLATION],
            description="Traduction live",
            io=AgentIO(input_schema={"text": "str", "target_lang": "str"}, output_schema={"translated": "str"}),
        ),
        AgentSpec(
            id="voice.qa",
            name="Voice QA",
            domain=AgentDomain.VOICE,
            skills=[AgentSkill.QA],
            description="Q&A RAG minute par minute",
            io=AgentIO(input_schema={"question": "str"}, output_schema={"answer": "str", "citations": "list"}),
        ),
        AgentSpec(
            id="mail.ingest",
            name="Mail Ingest",
            domain=AgentDomain.MAIL,
            skills=[AgentSkill.CLASSIFICATION],
            description="Ingestion Gmail/Outlook",
            io=AgentIO(input_schema={"provider": "str"}, output_schema={"threads": "list"}),
        ),
        AgentSpec(
            id="mail.classify",
            name="Mail Classify",
            domain=AgentDomain.MAIL,
            skills=[AgentSkill.CLASSIFICATION],
            description="Classement des emails",
            io=AgentIO(input_schema={"thread_id": "str"}, output_schema={"label": "str"}),
        ),
        AgentSpec(
            id="mail.summarize",
            name="Mail Summarize",
            domain=AgentDomain.MAIL,
            skills=[AgentSkill.SUMMARIZATION],
            description="Synthèse email",
            io=AgentIO(input_schema={"thread_id": "str"}, output_schema={"summary": "str", "risks": "list"}),
        ),
        AgentSpec(
            id="mail.replydraft",
            name="Mail Reply Draft",
            domain=AgentDomain.MAIL,
            skills=[AgentSkill.SUMMARIZATION],
            description="Rédaction brouillon",
            io=AgentIO(input_schema={"summary": "str"}, output_schema={"draft": "str"}),
        ),
        AgentSpec(
            id="mail.sender",
            name="Mail Sender",
            domain=AgentDomain.MAIL,
            skills=[AgentSkill.SUMMARIZATION],
            description="Envoi email avec HITL",
            io=AgentIO(input_schema={"draft_id": "str"}, output_schema={"status": "str"}),
        ),
        AgentSpec(
            id="rag.indexer",
            name="RAG Indexer",
            domain=AgentDomain.RAG,
            skills=[AgentSkill.RAG_INDEX],
            description="Indexation incrémentale",
            io=AgentIO(input_schema={"document": "str"}, output_schema={"chunks": "list"}),
        ),
        AgentSpec(
            id="rag.searcher",
            name="RAG Searcher",
            domain=AgentDomain.RAG,
            skills=[AgentSkill.RAG_SEARCH],
            description="Recherche hybride",
            io=AgentIO(input_schema={"query": "str"}, output_schema={"results": "list"}),
        ),
        AgentSpec(
            id="chat.agentcreator",
            name="Chat Agent Creator",
            domain=AgentDomain.CHAT,
            skills=[AgentSkill.QA],
            description="Création agent/UI/workflow",
            io=AgentIO(input_schema={"prompt": "str"}, output_schema={"spec": "dict"}),
        ),
        AgentSpec(
            id="coach.logingest",
            name="Coach Log Ingest",
            domain=AgentDomain.COACH,
            skills=[AgentSkill.HEALTH_ANALYTICS],
            description="Ingestion des logs santé",
            io=AgentIO(input_schema={"metric": "str"}, output_schema={"stored": "bool"}),
        ),
        AgentSpec(
            id="coach.reporter",
            name="Coach Reporter",
            domain=AgentDomain.COACH,
            skills=[AgentSkill.HEALTH_ANALYTICS],
            description="Rapports santé",
            io=AgentIO(input_schema={"logs": "list"}, output_schema={"report": "dict"}),
        ),
        AgentSpec(
            id="cr.builder",
            name="CR Builder",
            domain=AgentDomain.DOCS,
            skills=[AgentSkill.DOCUMENT_FORMATTING],
            description="Construction de comptes-rendus",
            io=AgentIO(input_schema={"meeting_id": "str"}, output_schema={"document_id": "str"}),
        ),
        AgentSpec(
            id="docs.formatter",
            name="Docs Formatter",
            domain=AgentDomain.DOCS,
            skills=[AgentSkill.DOCUMENT_FORMATTING],
            description="Génération PDF/LaTeX/Docx",
            io=AgentIO(input_schema={"structure": "dict"}, output_schema={"path": "str"}),
        ),
        AgentSpec(
            id="web.factchecker",
            name="Web Fact Checker",
            domain=AgentDomain.WEBINTEL,
            skills=[AgentSkill.FACT_CHECK],
            description="Score de confiance",
            io=AgentIO(input_schema={"claims": "list"}, output_schema={"verdicts": "list"}),
        ),
        AgentSpec(
            id="pm.riskminer",
            name="PM Risk Miner",
            domain=AgentDomain.PM,
            skills=[AgentSkill.PM_REPORTING],
            description="Extraction des risques",
            io=AgentIO(input_schema={"project_id": "str"}, output_schema={"risks": "list"}),
        ),
        AgentSpec(
            id="pm.report.codir",
            name="PM CODIR Reporter",
            domain=AgentDomain.PM,
            skills=[AgentSkill.PM_REPORTING],
            description="Reporting CODIR",
            io=AgentIO(input_schema={"project_id": "str"}, output_schema={"deck": "dict"}),
        ),
    ]

    for spec in default_agents:
        _registry.register(spec)


def get_registry() -> AgentRegistry:
    if not _registry.agents:
        seed_default_agents()
    return _registry


__all__ = ["AgentRegistry", "get_registry", "seed_default_agents"]
