import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api import dependencies  # noqa: E402
from models import AgentDomain, OrchestrationRequest  # noqa: E402


@pytest.mark.asyncio
async def test_master_orchestrator_executes_known_agent():
    orchestrator = dependencies.get_master_orchestrator()

    request = OrchestrationRequest(
        domain=AgentDomain.MAIL,
        objective="mail.summarize",
        payload={"thread_id": "demo-thread", "account_id": "demo"},
    )

    response = await orchestrator.execute(request)

    assert response.status == "accepted"
    executions = response.trace.result["executions"]
    assert any(exec_["agent_id"] == "mail.summarize" for exec_ in executions)
