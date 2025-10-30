"""Event bus abstraction using Redis Streams or NATS."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

try:
    import redis.asyncio as redis_async  # type: ignore
except ImportError:  # pragma: no cover
    redis_async = None  # type: ignore

from config import get_settings

logger = logging.getLogger(__name__)


class MessagingService:
    """Bus publication / requête basé sur Redis avec tampon local."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional["redis_async.Redis"] = None
        self._buffer: List[Dict[str, Any]] = []

    async def _get_client(self) -> Optional["redis_async.Redis"]:
        if self._client or not redis_async:
            return self._client
        try:
            self._client = redis_async.from_url(self.settings.messaging.url, encoding="utf-8", decode_responses=True)
        except Exception as exc:  # pragma: no cover
            logger.warning("Connexion Redis indisponible, fallback buffer", exc_info=exc)
            self._client = None
        return self._client

    async def publish(self, subject: str, payload: Dict[str, Any]) -> None:
        client = await self._get_client()
        if client:
            try:
                await client.publish(subject, json.dumps(payload, default=str))
                return
            except Exception as exc:  # pragma: no cover
                logger.error("Publication Redis échouée, fallback buffer", exc_info=exc)
        logger.info("[Messaging:fallback] publish", extra={"subject": subject})
        self._buffer.append({"subject": subject, "payload": payload})

    async def request(self, subject: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        client = await self._get_client()
        if client:
            try:
                stream = f"req:{subject}"
                entry_id = await client.xadd(stream, {"payload": json.dumps(payload, default=str)})
                return {"subject": subject, "status": "accepted", "entry_id": entry_id}
            except Exception as exc:  # pragma: no cover
                logger.error("Request Redis échouée, fallback buffer", exc_info=exc)
        logger.info("[Messaging:fallback] request", extra={"subject": subject})
        self._buffer.append({"subject": subject, "payload": payload, "kind": "request"})
        return {"subject": subject, "status": "buffered"}

    def buffered_events(self) -> List[Dict[str, Any]]:
        """Expose les messages tamponnés pour debug/monitoring."""
        return list(self._buffer)
