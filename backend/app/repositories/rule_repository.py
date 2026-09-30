from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.fraud_rule import FraudRule


class RuleRepository:
    """Repository handling persistence and configuration for Fraud Rules."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, rule: FraudRule) -> FraudRule:
        """Persist a new fraud rule configuration."""
        self.db.add(rule)
        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: str) -> Optional[FraudRule]:
        """Fetch rule configuration by internal ID."""
        stmt = select(FraudRule).where(FraudRule.id == rule_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(self, rule_code: str) -> Optional[FraudRule]:
        """Fetch rule configuration by business rule code."""
        stmt = select(FraudRule).where(FraudRule.rule_code == rule_code)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_rules(self, active_only: bool = False) -> List[FraudRule]:
        """Query rules."""
        stmt = select(FraudRule)
        if active_only:
            stmt = stmt.where(FraudRule.is_active.is_(True))
        stmt = stmt.order_by(desc(FraudRule.weight))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_rule(
        self,
        rule_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        weight: Optional[float] = None,
        is_active: Optional[bool] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Optional[FraudRule]:
        """Update an existing rule."""
        rule = await self.get_by_id(rule_id)
        if rule:
            if name is not None:
                rule.name = name
            if description is not None:
                rule.description = description
            if weight is not None:
                rule.weight = weight
            if is_active is not None:
                rule.is_active = is_active
            if parameters is not None:
                rule.parameters = parameters
            await self.db.flush()
            await self.db.refresh(rule)
        return rule

    async def delete(self, rule_id: str) -> bool:
        """Delete rule configuration."""
        rule = await self.get_by_id(rule_id)
        if rule:
            await self.db.delete(rule)
            await self.db.flush()
            return True
        return False
