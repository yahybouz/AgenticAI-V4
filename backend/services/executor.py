from __future__ import annotations

import asyncio
import time
import uuid
from typing import Dict, List

from agents import AgentRegistry
from models import AgentExecutionResult, AgentSpec
from services.database import DatabaseService


class AgentExecutor:
    """Executes agents locally (stub implementation)."""

    def __init__(
        self,
        registry: AgentRegistry,
        *,
        database: DatabaseService,
    ) -> None:
        self.registry = registry
        self.database = database

    async def execute(self, agent_id: str, payload: Dict[str, object]) -> AgentExecutionResult:
        agent = self.registry.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} introuvable")

        started_at = time.perf_counter()
        output, citations = await self._dispatch(agent, payload)
        latency_ms = int((time.perf_counter() - started_at) * 1000)
        trace_id = str(uuid.uuid4())

        await self.database.save_agent_execution(
            {
                "agent_id": agent_id,
                "latency_ms": latency_ms,
                "payload_keys": list(payload.keys()),
                "output_keys": list(output.keys()),
            }
        )

        return AgentExecutionResult(
            agent_id=agent_id,
            success=True,
            output=output,
            latency_ms=latency_ms,
            trace_id=trace_id,
            citations=citations,
        )

    async def _dispatch(self, agent: AgentSpec, payload: Dict[str, object]) -> tuple[Dict[str, object], List[Dict[str, str]]]:
        await asyncio.sleep(0)
        handler_name = agent.id.replace('.', '_')
        handler = getattr(self, f"_run_{handler_name}", None)
        if handler:
            return await handler(payload)
        return ({"message": f"{agent.name} exécuté"}, [])

    async def _run_voice_transcribe(self, payload):
        text = payload.get("text") or "Transcription en attente"
        return ({"text": text}, [])

    async def _run_voice_translate(self, payload):
        text = payload.get("text", "")
        target = payload.get("target_lang", "en")
        return ({"translated": f"[{target}] {text}"}, [])

    async def _run_voice_qa(self, payload):
        question = payload.get("question", "")
        answer = f"Réponse synthétique pour: {question}" if question else "Aucune question"
        citations = [{"source": "meeting://minute-01", "snippet": "Extrait pertinent"}]
        return ({"answer": answer}, citations)

    async def _run_mail_summarize(self, payload):
        thread_id = payload.get("thread_id", "unknown")
        summary = f"Synthèse du thread {thread_id}"
        return (
            {
                "summary": summary,
                "risks": ["Actions en attente"],
                "next_steps": ["Répondre avant 18h"],
            },
            [],
        )

    async def _run_mail_replydraft(self, payload):
        summary = payload.get("summary", "")
        draft = f"Bonjour,\n\n{summary}\n\nCordialement"
        return ({"draft": draft}, [])

    async def _run_mail_sender(self, payload):
        status = "sent" if payload.get("approve") else "pending_approval"
        return ({"status": status}, [])

    async def _run_rag_searcher(self, payload):
        query = payload.get("query", "")
        results = [
            {"text": f"Passage associé à {query}", "score": 0.82, "source": "kb://doc-1"}
        ]
        return ({"results": results}, [])

    async def _run_rag_indexer(self, payload):
        return ({"status": "indexed"}, [])

    async def _run_coach_logingest(self, payload):
        metric = payload.get("metric", "unknown")
        return ({"stored": True, "metric": metric}, [])

    async def _run_cr_builder(self, payload):
        meeting_id = payload.get("meeting_id", "meeting")
        return ({"document_id": f"cr-{meeting_id}"}, [])

    async def _run_docs_formatter(self, payload):
        return ({"path": "/tmp/cr-output.pdf"}, [])

    async def _run_web_factchecker(self, payload):
        claims = payload.get("claims", [])
        verdicts = [{"claim": claim, "verdict": "supported"} for claim in claims]
        citations = [{"source": "https://source.local", "snippet": "Citation"}] if claims else []
        return ({"verdicts": verdicts}, citations)

    async def _run_pm_riskminer(self, payload):
        project_id = payload.get("project_id", "proj")
        risks = [
            {"name": "Dérive planning", "severity": "high", "project": project_id}
        ]
        return ({"risks": risks}, [])

    async def _run_pm_report_codir(self, payload):
        project_id = payload.get("project_id", "proj")
        return ({"deck": {"project": project_id, "status": "green"}}, [])
