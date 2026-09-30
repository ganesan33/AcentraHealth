from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.services.fraud_service import FraudService
from app.schemas.fraud import (
    FraudEvaluationRequest,
    FraudEvaluationResponse,
    RuleResultItem,
    FraudDecisionEnum,
)

router = APIRouter(prefix="/fraud", tags=["Fraud Evaluation"])


@router.post("/evaluate", response_model=FraudEvaluationResponse, status_code=status.HTTP_200_OK)
async def evaluate_fraud(
    payload: FraudEvaluationRequest,
    db: AsyncSession = Depends(get_db),
) -> FraudEvaluationResponse:
    """
    Evaluate an incoming transaction payload against all enabled fraud rules,
    compute composite risk score, and generate routing decision (APPROVE, REVIEW, REJECT).
    """
    service = FraudService(db)
    raw_tx = payload.transaction.model_dump()
    eval_result = await service.evaluate_transaction(raw_tx, persist=True)

    return FraudEvaluationResponse(
        evaluation_id=str(uuid.uuid4()),
        transaction_id=eval_result.transaction_id,
        decision=FraudDecisionEnum(eval_result.decision.value),
        decision_state=eval_result.decision_state,
        verdict=eval_result.verdict,
        risk_score=eval_result.risk_score,
        triggered_rule_count=len(eval_result.triggered_rules),
        evaluation_time_ms=eval_result.evaluation_time_ms,
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
            for r in eval_result.triggered_rules
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
            for r in eval_result.all_rule_results
        ],
        evaluated_at=eval_result.metadata.get("timestamp") or eval_result.metadata.get("evaluated_at") or "2026-09-30T12:00:00Z",
        metadata_info=eval_result.metadata,
    )


@router.get("/evaluations/{evaluation_id}", status_code=status.HTTP_200_OK)
async def get_evaluation_by_id(
    evaluation_id: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve detailed execution results for an individual evaluation run."""
    service = FraudService(db)
    ev = await service.fraud_repo.get_evaluation_by_id(evaluation_id)
    if not ev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID '{evaluation_id}' was not found.",
        )
    return {
        "evaluation_id": ev.id,
        "transaction_id": ev.transaction_id,
        "decision": ev.final_decision,
        "risk_score": ev.risk_score,
        "triggered_rule_count": ev.triggered_rule_count,
        "evaluation_time_ms": ev.evaluation_time_ms,
        "evaluated_at": ev.evaluated_at,
        "rule_results": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "triggered": r.triggered,
                "score_impact": r.score_impact,
                "reason": r.reason,
                "metadata": r.rule_metadata,
            }
            for r in ev.rule_results
        ],
    }
