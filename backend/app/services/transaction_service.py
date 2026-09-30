from typing import List, Optional, Dict, Any
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.services.fraud_service import FraudService
from app.schemas.transaction import TransactionCreate
from app.schemas.fraud import FraudEvaluationResponse, RuleResultItem, FraudDecisionEnum


class TransactionService:
    """Service handling transaction ingestion, lifecycle, and fraud evaluation triggering."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.tx_repo = TransactionRepository(db)
        self.fraud_service = FraudService(db)

    async def ingest_transaction(
        self,
        payload: TransactionCreate,
        evaluate: bool = True,
    ) -> Dict[str, Any]:
        """
        Ingest a transaction: persists to database and evaluates for fraud.
        """
        tx_id = payload.id or str(uuid.uuid4())
        
        transaction = Transaction(
            id=tx_id,
            user_id=payload.user_id,
            account_id=payload.account_id,
            amount=payload.amount,
            currency=payload.currency,
            merchant_id=payload.merchant_id,
            merchant_category=payload.merchant_category,
            channel=payload.channel,
            ip_address=payload.ip_address,
            device_id=payload.device_id,
            location_city=payload.location_city,
            location_country=payload.location_country,
            latitude=payload.latitude,
            longitude=payload.longitude,
            status="PENDING",
        )
        saved_tx = await self.tx_repo.create(transaction)

        evaluation_output: Optional[FraudEvaluationResponse] = None
        if evaluate:
            raw_eval = await self.fraud_service.evaluate_transaction(payload.model_dump())
            evaluation_output = FraudEvaluationResponse(
                evaluation_id=str(uuid.uuid4()),
                transaction_id=tx_id,
                decision=FraudDecisionEnum(raw_eval.decision.value),
                decision_state=raw_eval.decision_state,
                verdict=raw_eval.verdict,
                risk_score=raw_eval.risk_score,
                triggered_rule_count=len(raw_eval.triggered_rules),
                evaluation_time_ms=raw_eval.evaluation_time_ms,
                triggered_rules=[
                    RuleResultItem(
                        rule_id=r.rule_id,
                        rule_name=r.rule_name,
                        triggered=r.triggered,
                        score_impact=r.score_impact,
                        reason=r.reason,
                        severity=r.severity,
                        status=r.status,
                        metadata=r.metadata,
                    )
                    for r in raw_eval.triggered_rules
                ],
                all_rule_results=[
                    RuleResultItem(
                        rule_id=r.rule_id,
                        rule_name=r.rule_name,
                        triggered=r.triggered,
                        score_impact=r.score_impact,
                        reason=r.reason,
                        severity=r.severity,
                        status=r.status,
                        metadata=r.metadata,
                    )
                    for r in raw_eval.all_rule_results
                ],
                evaluated_at=raw_eval.metadata.get("timestamp") or saved_tx.created_at,
                metadata_info=raw_eval.metadata,
            )

        return {
            "transaction": saved_tx,
            "evaluation": evaluation_output,
        }

    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Fetch transaction by ID."""
        return await self.tx_repo.get_by_id(transaction_id)

    async def list_transactions(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        account_id: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> List[Transaction]:
        """Query transactions with filtering."""
        return await self.tx_repo.list_transactions(
            limit=limit,
            offset=offset,
            status=status,
            user_id=user_id,
            account_id=account_id,
            min_amount=min_amount,
            max_amount=max_amount,
        )
