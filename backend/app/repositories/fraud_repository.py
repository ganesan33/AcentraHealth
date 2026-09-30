from typing import List, Optional
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.fraud_evaluation import FraudEvaluation
from app.models.rule_result import RuleResultModel


class FraudRepository:
    """Repository handling persistence and queries for fraud evaluations and rule outcomes."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_evaluation(self, evaluation: FraudEvaluation) -> FraudEvaluation:
        """Persist a new fraud evaluation record."""
        self.db.add(evaluation)
        await self.db.flush()
        await self.db.refresh(evaluation)
        return evaluation

    async def add_rule_results(self, results: List[RuleResultModel]) -> List[RuleResultModel]:
        """Bulk persist individual rule outcomes."""
        for r in results:
            self.db.add(r)
        await self.db.flush()
        return results

    async def get_evaluation_by_id(self, evaluation_id: str) -> Optional[FraudEvaluation]:
        """Fetch evaluation along with its rule result details."""
        stmt = (
            select(FraudEvaluation)
            .where(FraudEvaluation.id == evaluation_id)
            .options(selectinload(FraudEvaluation.rule_results))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_transaction_id(self, transaction_id: str) -> List[FraudEvaluation]:
        """Fetch all evaluations associated with a given transaction."""
        stmt = (
            select(FraudEvaluation)
            .where(FraudEvaluation.transaction_id == transaction_id)
            .options(selectinload(FraudEvaluation.rule_results))
            .order_by(desc(FraudEvaluation.evaluated_at))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_high_risk(self, min_score: float = 75.0, limit: int = 10) -> List[FraudEvaluation]:
        """Fetch recent high-risk flagged evaluations."""
        stmt = (
            select(FraudEvaluation)
            .where(FraudEvaluation.risk_score >= min_score)
            .options(
                selectinload(FraudEvaluation.rule_results),
                selectinload(FraudEvaluation.transaction),
            )
            .order_by(desc(FraudEvaluation.evaluated_at))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_average_risk_score(self) -> float:
        """Compute the average risk score across all recorded evaluations."""
        stmt = select(func.avg(FraudEvaluation.risk_score))
        result = await self.db.execute(stmt)
        val = result.scalar_one_or_none()
        return float(val) if val is not None else 0.0
