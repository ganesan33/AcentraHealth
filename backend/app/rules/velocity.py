import time
from collections import defaultdict, deque
from typing import Any, Dict, Optional
from app.rules.base import BaseFraudRule, RuleResult
from app.core.redis import get_redis
from app.core.logging import logger


class HighFrequencyTransactionRule(BaseFraudRule):
    """
    Velocity Fraud Rule: Detects rapid-fire transactions from the same user or card.
    Uses Redis sliding-window counter when connected, falling back to local memory if unavailable.
    """
    rule_id: str = "VELOCITY_BURST_10M"
    rule_name: str = "High Frequency Transaction Rule"
    description: str = "Flags rapid consecutive transactions for the same user within a short time window"
    weight: float = 35.0
    enabled: bool = True

    # In-memory sliding window fallback for environments without Redis
    _memory_window: Dict[str, deque] = defaultdict(deque)

    def __init__(self, max_allowed: int = 5, window_seconds: int = 600, weight: float = 35.0) -> None:
        self.max_allowed = max_allowed
        self.window_seconds = window_seconds
        self.weight = weight

    async def evaluate(self, transaction_data: Dict[str, Any]) -> RuleResult:
        user_id = str(transaction_data.get("user_id", ""))
        if not user_id or user_id == "unknown":
            return RuleResult(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                triggered=False,
                score_impact=0.0,
                reason="No user_id provided for velocity check",
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
                key = f"fraud:velocity:{user_id}"
                # Redis sliding window using sorted sets
                pipe = redis.pipeline()
                pipe.zremrangebyscore(key, 0, now - self.window_seconds)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, self.window_seconds)
                results = await pipe.execute()
                count = results[2]
            except Exception as e:
                logger.warning(f"Redis velocity check failed, using fallback: {e}")
                count = self._evaluate_in_memory(user_id, now)
        else:
            count = self._evaluate_in_memory(user_id, now)

        triggered = count > self.max_allowed
        reason = (
            f"User exceeded velocity threshold: {count} transactions in {self.window_seconds}s (limit: {self.max_allowed})"
            if triggered
            else f"Velocity normal: {count}/{self.max_allowed} transactions in window"
        )

        return RuleResult(
            rule_id=self.rule_id,
            rule_name=self.rule_name,
            triggered=triggered,
            score_impact=self.weight if triggered else 0.0,
            reason=reason,
            metadata={
                "transaction_count": count,
                "window_seconds": self.window_seconds,
                "limit": self.max_allowed,
                "user_id": user_id,
            },
        )

    def _evaluate_in_memory(self, user_id: str, now: float) -> int:
        dq = self._memory_window[user_id]
        cutoff = now - self.window_seconds
        while dq and dq[0] < cutoff:
            dq.popleft()
        dq.append(now)
        return len(dq)
