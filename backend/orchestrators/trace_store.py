from __future__ import annotations

from typing import Dict

from models import ExecutionTrace


class TraceStore:
    def __init__(self) -> None:
        self.traces: Dict[str, ExecutionTrace] = {}

    def add(self, trace: ExecutionTrace) -> None:
        self.traces[trace.trace_id] = trace

    def get(self, trace_id: str) -> ExecutionTrace | None:
        return self.traces.get(trace_id)

    def list_recent(self, limit: int = 20) -> list[ExecutionTrace]:
        return list(self.traces.values())[-limit:]


trace_store = TraceStore()
