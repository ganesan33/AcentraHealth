from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review


class ReviewRepository:
    """Repository handling analyst investigation review queue entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, review: Review) -> Review:
        """Add a transaction into the manual review queue."""
        self.db.add(review)
        await self.db.flush()
        await self.db.refresh(review)
        return review

    async def get_by_id(self, review_id: str) -> Optional[Review]:
        """Fetch review record by ID."""
        stmt = (
            select(Review)
            .where(Review.id == review_id)
            .options(selectinload(Review.transaction))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Review]:
        """Fetch review record for a specific transaction."""
        stmt = select(Review).where(Review.transaction_id == transaction_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_reviews(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        analyst: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Review]:
        """Query review queue items with filtering."""
        stmt = select(Review).options(selectinload(Review.transaction))

        if status:
            stmt = stmt.where(Review.status == status)
        if priority:
            stmt = stmt.where(Review.priority == priority)
        if analyst:
            stmt = stmt.where(Review.assigned_analyst == analyst)

        stmt = stmt.order_by(desc(Review.created_at)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_decision(
        self,
        review_id: str,
        decision: str,
        decision_reason: str,
        reviewer_notes: Optional[str] = None,
        analyst_id: Optional[str] = None,
    ) -> Optional[Review]:
        """Record manual review verdict."""
        review = await self.get_by_id(review_id)
        if review:
            review.status = decision if decision in ["APPROVED", "REJECTED", "ESCALATED"] else "REVIEWED"
            review.decision = decision
            review.decision_reason = decision_reason
            review.reviewer_notes = reviewer_notes
            review.assigned_analyst = analyst_id or review.assigned_analyst
            review.reviewed_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(review)
        return review

    async def count_by_status(self, status: Optional[str] = None) -> int:
        """Count review items by status."""
        stmt = select(func.count(Review.id))
        if status:
            stmt = stmt.where(Review.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one() or 0
