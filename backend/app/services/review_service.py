from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review
from app.repositories.review_repository import ReviewRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.audit_repository import AuditRepository
from app.schemas.review import ReviewUpdateDecision
from app.core.logging import logger


class ReviewService:
    """Service handling reviewer console workflow, decisions, and manual overrides."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.tx_repo = TransactionRepository(db)
        self.audit_repo = AuditRepository(db)

    async def list_pending_reviews(
        self,
        status: Optional[str] = "PENDING",
        priority: Optional[str] = None,
        analyst: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Review]:
        """Fetch cases waiting for investigation in the console queue."""
        return await self.review_repo.list_reviews(
            status=status,
            priority=priority,
            analyst=analyst,
            limit=limit,
            offset=offset,
        )

    async def get_review_by_id(self, review_id: str) -> Optional[Review]:
        """Fetch review record by ID."""
        return await self.review_repo.get_by_id(review_id)

    async def process_analyst_decision(
        self,
        review_id: str,
        payload: ReviewUpdateDecision,
        actor: str = "analyst",
    ) -> Optional[Review]:
        """
        Record analyst manual override decision, update transaction status, and record audit trail.
        """
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            return None

        previous_status = review.status
        updated_review = await self.review_repo.update_decision(
            review_id=review_id,
            decision=payload.decision.value,
            decision_reason=payload.decision_reason,
            reviewer_notes=payload.reviewer_notes,
            analyst_id=payload.analyst_id or actor,
        )

        # Update corresponding transaction status
        new_tx_status = "APPROVED" if payload.decision.value == "APPROVE" else "REJECTED"
        if payload.decision.value != "ESCALATE":
            await self.tx_repo.update_status(review.transaction_id, new_tx_status)

        # Record audit log
        await self.audit_repo.log(
            entity_type="REVIEW",
            entity_id=review_id,
            action="MANUAL_OVERRIDE",
            actor=actor,
            changes={
                "previous_status": previous_status,
                "new_decision": payload.decision.value,
                "reason": payload.decision_reason,
            },
            notes=payload.reviewer_notes,
        )
        logger.info(
            f"Review {review_id} decision submitted: {payload.decision.value} by {actor} for TX {review.transaction_id}"
        )

        return updated_review
