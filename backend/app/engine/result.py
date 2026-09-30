from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.rules.base import RuleResult


class FraudDecision(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class FraudEvaluationResult(BaseModel):
    """Overall evaluation output produced by the Fraud Engine."""
    transaction_id: str
    decision: FraudDecision
    risk_score: float = Field(ge=0.0, le=100.0, description="Risk score between 0 and 100")
    triggered_rules: List[RuleResult] = []
    all_rule_results: List[RuleResult] = []
    metadata: Dict[str, Any] = {}
    evaluation_time_ms: float = 0.0
