from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.transaction import Transaction


class TransactionRepository:
    """Repository handling persistence and queries for Transaction entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, transaction: Transaction) -> Transaction:
        """Persist a new transaction entity."""
        self.db.add(transaction)
        await self.db.flush()
        await self.db.refresh(transaction)
        return transaction

    async def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Fetch a single transaction by ID."""
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_transactions(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        account_id: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> List[Transaction]:
        """Query transactions with filtering and pagination."""
        stmt = select(Transaction)

        if status:
            stmt = stmt.where(Transaction.status == status)
        if user_id:
            stmt = stmt.where(Transaction.user_id == user_id)
        if account_id:
            stmt = stmt.where(Transaction.account_id == account_id)
        if min_amount is not None:
            stmt = stmt.where(Transaction.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Transaction.amount <= max_amount)

        stmt = stmt.order_by(desc(Transaction.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_total(self, status: Optional[str] = None) -> int:
        """Count total transactions matching optional status."""
        stmt = select(func.count(Transaction.id))
        if status:
            stmt = stmt.where(Transaction.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0

    async def update_status(self, transaction_id: str, new_status: str) -> Optional[Transaction]:
        """Update transaction processing state."""
        tx = await self.get_by_id(transaction_id)
        if tx:
            tx.status = new_status
            await self.db.flush()
            await self.db.refresh(tx)
        return tx
