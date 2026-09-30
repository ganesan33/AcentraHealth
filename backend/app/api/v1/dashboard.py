from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardMetricsResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard Metrics"])


@router.get("/summary", response_model=DashboardMetricsResponse, status_code=status.HTTP_200_OK)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
) -> DashboardMetricsResponse:
    """Retrieve executive metrics, risk aggregates, and recent alert feed for the dashboard."""
    service = DashboardService(db)
    return await service.get_dashboard_summary()
