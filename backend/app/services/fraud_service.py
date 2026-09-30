from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.engine.fraud_engine import FraudEngine
from app.engine.result import FraudEvaluationResult, FraudDecision
from app.models.fraud_evaluation import FraudEvaluation
from app.models.rule_result import RuleResultModel
from app.models.review import Review
from app.repositories.fraud_repository import FraudRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.review_repository import ReviewRepository
from app.services.notification_service import NotificationService
from app.core.logging import logger


class FraudService:
    """Service orchestrating fraud evaluation, persistence, review queueing, and alerts."""

    def __init__(
        self,
        db: AsyncSession,
        fraud_engine: Optional[FraudEngine] = None,
        notification_service: Optional[NotificationService] = None,
    ) -> None:
        self.db = db
        self.engine = fraud_engine or FraudEngine()
        self.fraud_repo = FraudRepository(db)
        self.tx_repo = TransactionRepository(db)
        self.review_repo = ReviewRepository(db)
        self.notifications = notification_service or NotificationService()

    async def evaluate_transaction(
        self,
        transaction_payload: Dict[str, Any],
        persist: bool = True,
    ) -> FraudEvaluationResult:
        """
        Evaluate a transaction against all enabled rules, compute decision,
        persist records if required, and route to reviewer queue if necessary.
        """
        tx_id = str(transaction_payload.get("id") or transaction_payload.get("transaction_id") or uuid.uuid4())
        transaction_payload["id"] = tx_id

        # 1. Run rule engine evaluation
        eval_result = await self.engine.evaluate_transaction(transaction_payload)

        if not persist:
            return eval_result

        # 2. Persist evaluation record
        evaluation_record = FraudEvaluation(
            id=str(uuid.uuid4()),
            transaction_id=tx_id,
            final_decision=eval_result.decision.value,
            risk_score=eval_result.risk_score,
            triggered_rule_count=len(eval_result.triggered_rules),
            evaluation_time_ms=eval_result.evaluation_time_ms,
            metadata_info=eval_result.metadata,
        )
        await self.fraud_repo.create_evaluation(evaluation_record)

        # 3. Persist individual rule results
        rule_models = [
            RuleResultModel(
                id=str(uuid.uuid4()),
                evaluation_id=evaluation_record.id,
                rule_id=res.rule_id,
                rule_name=res.rule_name,
                triggered=res.triggered,
                score_impact=res.score_impact,
                reason=res.reason,
                rule_metadata=res.metadata,
            )
            for res in eval_result.all_rule_results
        ]
        await self.fraud_repo.add_rule_results(rule_models)

        # 4. Update transaction status in DB if transaction exists
        tx = await self.tx_repo.get_by_id(tx_id)
        if tx:
            tx.status = eval_result.decision.value
            await self.tx_repo.update_status(tx_id, eval_result.decision.value)

        # 5. If decision is REVIEW, create an entry in the Review Queue
        if eval_result.decision == FraudDecision.REVIEW:
            existing_review = await self.review_repo.get_by_transaction_id(tx_id)
            if not existing_review:
                priority = "HIGH" if eval_result.risk_score >= 60.0 else "MEDIUM"
                review_item = Review(
                    id=str(uuid.uuid4()),
                    transaction_id=tx_id,
                    evaluation_id=evaluation_record.id,
                    status="PENDING",
                    priority=priority,
                )
                await self.review_repo.create(review_item)
                logger.info(f"Transaction {tx_id} queued for manual analyst review with priority {priority}.")

        # 6. If high risk, trigger notification alert
        if eval_result.risk_score >= 40.0:
            await self.notifications.send_fraud_alert(
                transaction_id=tx_id,
                risk_score=eval_result.risk_score,
                decision=eval_result.decision.value,
                details={
                    "triggered_rules": [r.rule_name for r in eval_result.triggered_rules],
                    "amount": transaction_payload.get("amount"),
                    "user_id": transaction_payload.get("user_id"),
                },
            )

        return eval_result
