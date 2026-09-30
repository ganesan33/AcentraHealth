from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


class AuditRepository:
    """Repository handling immutable audit trail entries."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor: str,
        changes: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
    ) -> AuditLog:
        """Create a new immutable audit record."""
        audit_entry = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor=actor,
            changes=changes,
            notes=notes,
        )
        self.db.add(audit_entry)
        await self.db.flush()
        await self.db.refresh(audit_entry)
        return audit_entry

    async def get_by_entity(self, entity_type: str, entity_id: str) -> List[AuditLog]:
        """Fetch audit trail for a specific entity."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .order_by(desc(AuditLog.timestamp))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_recent(self, limit: int = 50) -> List[AuditLog]:
        """Fetch most recent audit actions across the system."""
        stmt = select(AuditLog).order_by(desc(AuditLog.timestamp)).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
