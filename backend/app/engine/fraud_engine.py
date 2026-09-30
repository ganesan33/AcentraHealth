import time
from typing import Dict, Any, List
from app.rules.registry import RuleRegistry, rule_registry
from app.rules.base import RuleResult
from app.engine.risk_scorer import RiskScorer
from app.engine.result import FraudEvaluationResult, FraudDecision
from app.core.logging import logger


class FraudEngine:
    """
    Main Fraud Engine orchestrating rule retrieval, execution, and risk scoring.
    Skeleton implementation for project structure.
    """

    def __init__(
        self,
        registry: RuleRegistry = rule_registry,
        scorer: RiskScorer = RiskScorer(),
    ) -> None:
        self.registry = registry
        self.scorer = scorer

    async def evaluate_transaction(self, transaction: Dict[str, Any]) -> FraudEvaluationResult:
        """
        Evaluate a transaction against all enabled rules and compute decision.
        """
        start_time = time.time()
        transaction_id = str(transaction.get("id", transaction.get("transaction_id", "unknown")))
        
        enabled_rules = self.registry.get_enabled_rules()
        logger.info(f"Evaluating transaction {transaction_id} against {len(enabled_rules)} rules.")

        rule_results: List[RuleResult] = []
        triggered_rules: List[RuleResult] = []

        for rule in enabled_rules:
            try:
                res = await rule.evaluate(transaction)
                rule_results.append(res)
                if res.triggered:
                    triggered_rules.append(res)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")

        risk_score = self.scorer.calculate_score(rule_results)
        decision = self.scorer.determine_decision(risk_score)
        eval_time_ms = (time.time() - start_time) * 1000

        return FraudEvaluationResult(
            transaction_id=transaction_id,
            decision=decision,
            risk_score=risk_score,
            triggered_rules=triggered_rules,
            all_rule_results=rule_results,
            evaluation_time_ms=eval_time_ms,
        )
