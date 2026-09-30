from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class RuleResult(BaseModel):
    """Result returned by an individual fraud rule evaluation."""
    rule_id: str
    rule_name: str
    triggered: bool
    score_impact: float = 0.0
    reason: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseFraudRule(ABC):
    """Abstract base class for all Fraud Rules in the engine."""
    
    rule_id: str
    rule_name: str
    description: str = ""
    weight: float = 1.0
    enabled: bool = True

    @abstractmethod
    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        """
        Evaluates a transaction against this rule.
        Must be implemented by concrete rule classes.
        """
        pass
