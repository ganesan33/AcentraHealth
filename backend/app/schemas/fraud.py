from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.transaction import TransactionCreate


class FraudDecisionEnum(str, Enum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class RuleResultItem(BaseModel):
    """Schema for individual rule evaluation result within a response."""
    rule_id: str
    rule_name: str
    triggered: bool
    score_impact: float = 0.0
    reason: Optional[str] = None
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class FraudEvaluationRequest(BaseModel):
    """Request payload to evaluate an incoming transaction for fraud."""
    transaction: TransactionCreate
    rule_overrides: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional ad-hoc rule parameter overrides for simulation or testing",
    )


class FraudEvaluationResponse(BaseModel):
    """Full evaluation response produced by the Fraud Engine."""
    evaluation_id: str
    transaction_id: str
    decision: FraudDecisionEnum
    risk_score: float = Field(ge=0.0, le=100.0)
    triggered_rule_count: int
    evaluation_time_ms: float
    triggered_rules: List[RuleResultItem] = []
    all_rule_results: List[RuleResultItem] = []
    evaluated_at: datetime
    metadata_info: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
