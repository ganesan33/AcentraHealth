from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DashboardTrendPoint(BaseModel):
    """Aggregate volume and risk metrics for a specific timestamp bucket."""
    timestamp: str
    total_volume: int
    flagged_count: int
    avg_risk_score: float


class RecentAlertItem(BaseModel):
    """High-risk alert item displayed in the live console feed."""
    alert_id: str
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    risk_score: float
    decision: str
    triggered_rules: List[str]
    timestamp: datetime


class DashboardMetricsResponse(BaseModel):
    """High-level summary of fraud engine operations and queue states."""
    total_transactions: int = Field(..., description="Total transactions processed")
    flagged_fraud: int = Field(..., description="Transactions flagged as REJECT")
    under_review: int = Field(..., description="Transactions currently in REVIEW queue")
    approved_count: int = Field(..., description="Transactions APPROVED")
    approval_rate: float = Field(..., description="Percentage of approved transactions (0-100%)")
    average_risk_score: float = Field(..., description="Mean risk score across all evaluations")
    recent_alerts: List[RecentAlertItem] = Field(default=[], description="Recent suspicious events")
    trends: List[DashboardTrendPoint] = Field(default=[], description="Historical transaction trends")
