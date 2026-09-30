from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.fraud_repository import FraudRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.dashboard import DashboardMetricsResponse, RecentAlertItem, DashboardTrendPoint


class DashboardService:
    """Service computing consolidated KPIs and live feeds for the Analyst Dashboard."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.tx_repo = TransactionRepository(db)
        self.fraud_repo = FraudRepository(db)
        self.review_repo = ReviewRepository(db)

    async def get_dashboard_summary(self) -> DashboardMetricsResponse:
        """Aggregate platform KPIs and review metrics."""
        total_tx = await self.tx_repo.count_total()
        flagged_fraud = await self.tx_repo.count_total(status="REJECT")
        approved_count = await self.tx_repo.count_total(status="APPROVE")
        under_review = await self.review_repo.count_by_status(status="PENDING")
        avg_score = await self.fraud_repo.get_average_risk_score()

        approval_rate = (approved_count / total_tx * 100.0) if total_tx > 0 else 100.0

        # Query recent high-risk events
        recent_evals = await self.fraud_repo.get_recent_high_risk(min_score=50.0, limit=5)
        recent_alerts: List[RecentAlertItem] = []
        for ev in recent_evals:
            tx = ev.transaction
            recent_alerts.append(
                RecentAlertItem(
                    alert_id=ev.id,
                    transaction_id=ev.transaction_id,
                    user_id=tx.user_id if tx else "unknown",
                    amount=tx.amount if tx else 0.0,
                    currency=tx.currency if tx else "USD",
                    risk_score=ev.risk_score,
                    decision=ev.final_decision,
                    triggered_rules=[r.rule_name for r in ev.rule_results if r.triggered],
                    timestamp=ev.evaluated_at,
                )
            )

        # Baseline trend point
        trends = [
            DashboardTrendPoint(
                timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:00"),
                total_volume=total_tx,
                flagged_count=flagged_fraud,
                avg_risk_score=round(avg_score, 1),
            )
        ]

        return DashboardMetricsResponse(
            total_transactions=total_tx,
            flagged_fraud=flagged_fraud,
            under_review=under_review,
            approved_count=approved_count,
            approval_rate=round(approval_rate, 2),
            average_risk_score=round(avg_score, 2),
            recent_alerts=recent_alerts,
            trends=trends,
        )
