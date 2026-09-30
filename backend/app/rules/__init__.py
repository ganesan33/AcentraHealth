from app.rules.base import BaseFraudRule, RuleResult
from app.rules.registry import rule_registry, RuleRegistry
from app.rules.velocity import HighFrequencyTransactionRule
from app.rules.unusual_amount import UnusualAmountRule
from app.rules.impossible_location import ImpossibleLocationRule

# Auto-register standard rules if registry is empty
if not rule_registry.get_all_rules():
    rule_registry.register(HighFrequencyTransactionRule())
    rule_registry.register(UnusualAmountRule())
    rule_registry.register(ImpossibleLocationRule())

__all__ = [
    "BaseFraudRule",
    "RuleResult",
    "rule_registry",
    "RuleRegistry",
    "HighFrequencyTransactionRule",
    "UnusualAmountRule",
    "ImpossibleLocationRule",
]
