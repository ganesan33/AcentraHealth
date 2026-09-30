import time
from typing import Dict, Any, List
from app.rules.registry import RuleRegistry, rule_registry
from app.rules.base import RuleResult
from app.engine.risk_scorer import RiskScorer
from app.engine.result import FraudEvaluationResult, FraudDecision
from app.core.logging import logger


class FraudEngine:
    """
    Main Fraud Engine orchestrating rule retrieval, execution, policy evaluation, and risk scoring.
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
        Evaluate a transaction against all enabled rules and compute decision, decision_state, and verdict.
        """
        start_time = time.time()
        transaction_id = str(transaction.get("id", transaction.get("transaction_id", "unknown")))
        
        enabled_rules = self.registry.get_enabled_rules()
        logger.info(f"Evaluating transaction {transaction_id} against {len(enabled_rules)} rules.")

        rule_results: List[RuleResult] = []
        triggered_rules: List[RuleResult] = []

        for rule in enabled_rules:
            # Skip R10 in first pass so it can evaluate the cumulative score of all rules
            if rule.rule_id == "R10":
                continue
            try:
                res = await rule.evaluate(transaction)
                rule_results.append(res)
                if res.triggered:
                    triggered_rules.append(res)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")

        # Compute preliminary cumulative score
        risk_score = self.scorer.calculate_score(rule_results)

        # Evaluate R10 (Cumulative Fraud Score Threshold) with the computed score
        r10_rule = self.registry.get_rule("R10")
        if r10_rule and r10_rule.enabled:
            tx_with_score = dict(transaction)
            tx_with_score["risk_score"] = risk_score
            try:
                r10_res = await r10_rule.evaluate(tx_with_score)
                rule_results.append(r10_res)
                if r10_res.triggered:
                    triggered_rules.append(r10_res)
            except Exception as e:
                logger.error(f"Error evaluating R10: {e}")

        # Determine final decision, decision_state, and verdict
        decision, decision_state, verdict = self.scorer.determine_decision_and_state(risk_score, rule_results)
        eval_time_ms = (time.time() - start_time) * 1000

        return FraudEvaluationResult(
            transaction_id=transaction_id,
            decision=decision,
            decision_state=decision_state,
            verdict=verdict,
            risk_score=risk_score,
            triggered_rules=triggered_rules,
            all_rule_results=rule_results,
            metadata={
                "decision_state": decision_state,
                "verdict": verdict,
                "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
            evaluation_time_ms=eval_time_ms,
        )
