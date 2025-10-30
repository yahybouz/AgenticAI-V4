from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_monitoring_service

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.get("/insights")
async def insights(service=Depends(get_monitoring_service)):
    return await service.recent_insights()
