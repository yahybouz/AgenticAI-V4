from __future__ import annotations

from typing import Any, Dict

from models import OrchestrationResponse


def extract_output(response: OrchestrationResponse, agent_id: str) -> Dict[str, Any]:
    executions = response.trace.result.get("executions", []) if isinstance(response.trace.result, dict) else []
    for execution in executions:
        if execution.get("agent_id") == agent_id:
            return execution.get("output", {})
    return {}
