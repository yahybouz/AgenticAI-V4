"""Monitoring pipeline facade."""
from __future__ import annotations

import logging
from typing import List

from models import MetricSample, MonitoringInsight

logger = logging.getLogger(__name__)


class MonitoringService:
    async def collect(self, samples: List[MetricSample]) -> None:
        logger.info("[Monitoring] collect", extra={"count": len(samples)})

    async def recent_insights(self) -> List[MonitoringInsight]:
        logger.info("[Monitoring] insights request")
        return []
