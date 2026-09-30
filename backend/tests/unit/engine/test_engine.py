import pytest
from app.engine.fraud_engine import FraudEngine
from app.engine.risk_scorer import RiskScorer
from app.engine.result import FraudDecision
from app.rules.base import RuleResult


def test_risk_scorer_boundaries() -> None:
    """Verify decision thresholds for APPROVE, REVIEW, and REJECT."""
    scorer = RiskScorer(review_threshold=40.0, reject_threshold=75.0)

    # Approve boundary
    assert scorer.determine_decision(15.0) == FraudDecision.APPROVE
    assert scorer.determine_decision(39.9) == FraudDecision.APPROVE

    # Review boundary
    assert scorer.determine_decision(40.0) == FraudDecision.REVIEW
    assert scorer.determine_decision(74.9) == FraudDecision.REVIEW

    # Reject boundary
    assert scorer.determine_decision(75.0) == FraudDecision.REJECT
    assert scorer.determine_decision(100.0) == FraudDecision.REJECT


def test_risk_scorer_calculation() -> None:
    """Verify score calculation sums triggered impacts and bounds between 0 and 100."""
    scorer = RiskScorer()
    results = [
        RuleResult(rule_id="R1", rule_name="Rule 1", triggered=True, score_impact=30.0),
        RuleResult(rule_id="R2", rule_name="Rule 2", triggered=False, score_impact=50.0),
        RuleResult(rule_id="R3", rule_name="Rule 3", triggered=True, score_impact=20.0),
    ]
    assert scorer.calculate_score(results) == 50.0


@pytest.mark.asyncio
async def test_fraud_engine_orchestration() -> None:
    """Test full fraud evaluation pipeline runs and returns typed result."""
    engine = FraudEngine()
    tx = {
        "id": "tx_eval_101",
        "user_id": "usr_safe",
        "amount": 45.0,
        "currency": "USD",
    }
    result = await engine.evaluate_transaction(tx)
    assert result.transaction_id == "tx_eval_101"
    assert result.decision in [FraudDecision.APPROVE, FraudDecision.REVIEW, FraudDecision.REJECT]
    assert isinstance(result.risk_score, float)
    assert result.evaluation_time_ms >= 0.0
    assert len(result.all_rule_results) >= 3
