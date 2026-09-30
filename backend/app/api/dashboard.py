from fastapi import APIRouter, status
from typing import Dict, Any

router = APIRouter(prefix="/dashboard", tags=["Dashboard Metrics"])


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_dashboard_summary() -> Dict[str, Any]:
    """Placeholder endpoint for high-level dashboard fraud statistics."""
    return {
        "total_transactions": 0,
        "flagged_fraud": 0,
        "under_review": 0,
        "approval_rate": 100.0,
        "recent_alerts": [],
    }
