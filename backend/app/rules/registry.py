from typing import Dict, Type, List
from app.rules.base import BaseFraudRule
from app.core.logging import logger


class RuleRegistry:
    """Registry to register and maintain all active Fraud Rules."""
    
    def __init__(self) -> None:
        self._rules: Dict[str, BaseFraudRule] = {}

    def register(self, rule: BaseFraudRule) -> None:
        """Register a new fraud rule instance."""
        if rule.rule_id in self._rules:
            logger.warning(f"Overwriting rule with ID: {rule.rule_id}")
        self._rules[rule.rule_id] = rule
        logger.info(f"Registered rule: {rule.rule_id} - {rule.rule_name}")

    def unregister(self, rule_id: str) -> None:
        """Remove a rule from registry by ID."""
        if rule_id in self._rules:
            del self._rules[rule_id]

    def get_rule(self, rule_id: str) -> BaseFraudRule:
        """Fetch a registered rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[BaseFraudRule]:
        """Return all registered rule instances."""
        return list(self._rules.values())

    def get_enabled_rules(self) -> List[BaseFraudRule]:
        """Return all currently enabled rules."""
        return [rule for rule in self._rules.values() if rule.enabled]


# Global rule registry singleton instance
rule_registry = RuleRegistry()
