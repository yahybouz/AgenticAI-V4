"""Simplified Postgres access layer avec repli en mémoire."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

try:
    import asyncpg  # type: ignore
except ImportError:  # pragma: no cover - dépendance optionnelle
    asyncpg = None  # type: ignore

from config import get_settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Accès Postgres minimal avec fallback mémoire si la connexion échoue."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._pool: Optional["asyncpg.Pool"] = None
        self._executions: List[Dict[str, Any]] = []
        self._health_logs: List[Dict[str, Any]] = []
        self._templates: Dict[str, List[Dict[str, Any]]] = {
            "cr": [
                {
                    "id": "tpl-cr-default",
                    "name": "CR Standard",
                    "body": "## Décisions\n- ...\n## Actions\n- ...",
                }
            ]
        }

    async def _ensure_pool(self) -> Optional["asyncpg.Pool"]:
        if self._pool or not asyncpg:
            return self._pool
        try:
            self._pool = await asyncpg.create_pool(self.settings.database.postgres_url, min_size=1, max_size=5)
            logger.info("Pool Postgres initialisé")
        except Exception as exc:  # pragma: no cover - dépend réseau
            logger.warning("Connexion Postgres indisponible, fallback mémoire actif", exc_info=exc)
            self._pool = None
        return self._pool

    async def fetch_health_logs(self, user_id: str) -> List[Dict[str, Any]]:
        pool = await self._ensure_pool()
        if pool:
            try:
                rows = await pool.fetch(
                    "SELECT ts, type, value, note FROM health_logs WHERE user_id=$1 ORDER BY ts DESC LIMIT 100",
                    user_id,
                )
                return [dict(row) for row in rows]
            except Exception as exc:
                logger.error("Lecture health_logs échouée, fallback mémoire", exc_info=exc)
        return [log for log in self._health_logs if log.get("user_id") == user_id]

    async def save_agent_execution(self, record: Dict[str, Any]) -> None:
        pool = await self._ensure_pool()
        if pool:
            try:
                await pool.execute(
                    "INSERT INTO agent_executions(agent_id, payload, latency_ms) VALUES ($1, $2, $3)",
                    record.get("agent_id"),
                    json.dumps(record),
                    record.get("latency_ms"),
                )
                return
            except Exception as exc:
                logger.error("Echec insertion agent_executions, fallback mémoire", exc_info=exc)
        self._executions.append(record)

    async def list_templates(self, kind: str) -> List[Dict[str, Any]]:
        pool = await self._ensure_pool()
        if pool:
            try:
                rows = await pool.fetch(
                    "SELECT id, name, body FROM templates WHERE kind=$1 ORDER BY updated_at DESC LIMIT 20",
                    kind,
                )
                return [dict(row) for row in rows]
            except Exception as exc:
                logger.error("Lecture templates échouée, fallback mémoire", exc_info=exc)
        return self._templates.get(kind, [])
