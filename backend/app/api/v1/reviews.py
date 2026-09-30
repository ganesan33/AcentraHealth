from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.review_service import ReviewService
from app.schemas.review import ReviewRead, ReviewUpdateDecision
from app.core.security import get_current_user_claims

router = APIRouter(prefix="/reviews", tags=["Review Queue"])


@router.get("/", response_model=List[ReviewRead], status_code=status.HTTP_200_OK)
async def list_pending_reviews(
    status_filter: Optional[str] = Query("PENDING", alias="status"),
    priority: Optional[str] = Query(None),
    analyst: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[ReviewRead]:
    """List pending or active reviewer cases for manual analyst inspection."""
    service = ReviewService(db)
    items = await service.list_pending_reviews(
        status=status_filter,
        priority=priority,
        analyst=analyst,
        limit=limit,
        offset=offset,
    )
    return [ReviewRead.model_validate(item) for item in items]


@router.get("/{review_id}", response_model=ReviewRead, status_code=status.HTTP_200_OK)
async def get_review_details(
    review_id: str,
    db: AsyncSession = Depends(get_db),
) -> ReviewRead:
    """Retrieve full details of an individual review case."""
    service = ReviewService(db)
    review = await service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review case with ID '{review_id}' was not found.",
        )
    return ReviewRead.model_validate(review)


@router.post("/{review_id}/decision", response_model=ReviewRead, status_code=status.HTTP_200_OK)
async def submit_review_decision(
    review_id: str,
    payload: ReviewUpdateDecision,
    db: AsyncSession = Depends(get_db),
    claims: Dict[str, Any] = Depends(get_current_user_claims),
) -> ReviewRead:
    """Submit a reviewer verdict (APPROVE, REJECT, ESCALATE) and apply manual override."""
    service = ReviewService(db)
    actor = claims.get("sub", "analyst")
    updated_review = await service.process_analyst_decision(
        review_id=review_id,
        payload=payload,
        actor=actor,
    )
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review case with ID '{review_id}' was not found.",
        )
    return ReviewRead.model_validate(updated_review)
