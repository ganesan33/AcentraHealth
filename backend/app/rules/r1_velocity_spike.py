import time
from collections import defaultdict, deque
from typing import Any, Dict
from app.rules.base import BaseFraudRule, RuleResult
from app.core.redis import get_redis
from app.core.logging import logger


class HighVelocitySpikeRule(BaseFraudRule):
    """
    R1: High Velocity Spike Rule.
    Detects rapid successive transactions or velocity bursts on a card or user account
    within a short sliding window (default: >= 5 transactions within 600s / 10m).
    """
    rule_id: str = "R1"
    rule_name: str = "High Velocity Spike"
    description: str = "Detects rapid-fire consecutive transactions and velocity spikes on a card or user account"
    weight: float = 35.0
    enabled: bool = True

    # In-memory sliding window fallback
    _memory_window: Dict[str, deque] = defaultdict(deque)

    def __init__(self, max_allowed: int = 5, window_seconds: int = 600, weight: float = 35.0) -> None:
        self.max_allowed = max_allowed
        self.window_seconds = window_seconds
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        # Check explicit flags first (e.g. from upstream graph or case trigger)
        explicit_count = transaction_data.get("velocity_count") or transaction_data.get("total_transactions_count")
        flagged_count = transaction_data.get("flagged_transactions_count", 0)

        if explicit_count is not None and isinstance(explicit_count, (int, float)):
            count = int(explicit_count)
            triggered = count >= self.max_allowed or flagged_count >= 3
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                triggered=triggered,
                status="TRIGGERED" if triggered else "NOT_TRIGGERED",
                severity="CRITICAL" if count >= 7 else "HIGH",
                score_impact=self.weight if triggered else 0.0,
                reason=(
                    f"High velocity spike detected: {count} transactions recorded (limit: {self.max_allowed})"
                    if triggered
                    else f"Velocity normal: {count} transactions recorded"
                ),
                metadata={"transaction_count": count, "limit": self.max_allowed, "window_seconds": self.window_seconds},
            )

        # Sliding window based on user_id or card_id / account_id
        entity_key = str(
            transaction_data.get("card_id")
            or transaction_data.get("user_id")
            or transaction_data.get("account_id")
            or ""
        )
        if not entity_key or entity_key == "unknown":
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                triggered=False,
                status="NOT_TRIGGERED",
                severity="INFO",
                score_impact=0.0,
                reason="No user or card identifier available for velocity tracking",
            )

        now = time.time()
        count = 0
        redis = None
        try:
            redis = await get_redis()
        except Exception:
            redis = None

        if redis:
            try:
                key = f"fraud:r1_velocity:{entity_key}"
                pipe = redis.pipeline()
                pipe.zremrangebyscore(key, 0, now - self.window_seconds)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, self.window_seconds)
                results = await pipe.execute()
                count = results[2]
            except Exception as e:
                logger.warning(f"Redis velocity check failed in R1, using in-memory fallback: {e}")
                count = self._evaluate_in_memory(entity_key, now)
        else:
            count = self._evaluate_in_memory(entity_key, now)

        triggered = count >= self.max_allowed
        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=triggered,
            status="TRIGGERED" if triggered else "NOT_TRIGGERED",
            severity="CRITICAL" if count >= self.max_allowed + 2 else "HIGH",
            score_impact=self.weight if triggered else 0.0,
            reason=(
                f"High velocity spike: {count} transactions detected in {self.window_seconds}s (threshold: >= {self.max_allowed})"
                if triggered
                else f"Transaction velocity within nominal parameters: {count}/{self.max_allowed}"
            ),
            metadata={"entity_key": entity_key, "count": count, "window_seconds": self.window_seconds},
        )

    def _evaluate_in_memory(self, key: str, now: float) -> int:
        dq = self._memory_window[key]
        cutoff = now - self.window_seconds
        while dq and dq[0] < cutoff:
            dq.popleft()
        dq.append(now)
        return len(dq)


__all__ = ["HighVelocitySpikeRule"]
