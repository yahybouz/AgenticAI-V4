"""Monitoring data contracts."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal

from pydantic import BaseModel, Field


class MetricScope(str, Enum):
    VOICE = "voice"
    EMAIL = "email"
    RAG = "rag"
    DOCS = "docs"
    PM = "pm"
    WEBINTEL = "webintel"


class MetricSample(BaseModel):
    metric: str
    value: float
    target: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = Field(default_factory=dict)


class MonitoringRule(BaseModel):
    name: str
    condition: str
    action: str
    scope: MetricScope


class MonitoringInsight(BaseModel):
    scope: MetricScope
    description: str
    severity: Literal["info", "warning", "critical"]
    samples: List[MetricSample] = Field(default_factory=list)

