from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ReviewStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


class ReviewPriorityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReviewDecisionEnum(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


class ReviewCreate(BaseModel):
    """Schema for creating a manual review queue entry."""
    transaction_id: str
    evaluation_id: Optional[str] = None
    priority: ReviewPriorityEnum = ReviewPriorityEnum.MEDIUM
    assigned_analyst: Optional[str] = None
    reviewer_notes: Optional[str] = None


class ReviewUpdateDecision(BaseModel):
    """Schema submitted by an analyst when overriding or approving a flagged transaction."""
    decision: ReviewDecisionEnum = Field(..., description="Analyst decision: APPROVE, REJECT, or ESCALATE")
    decision_reason: str = Field(..., min_length=3, description="Justification for the decision")
    reviewer_notes: Optional[str] = Field(default=None, description="Detailed analyst investigation notes")
    analyst_id: Optional[str] = Field(default=None, description="Identifier of the reviewer")


class ReviewRead(BaseModel):
    """Schema returned when reading a review item."""
    id: str
    transaction_id: str
    evaluation_id: Optional[str] = None
    status: ReviewStatusEnum
    priority: ReviewPriorityEnum
    assigned_analyst: Optional[str] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
