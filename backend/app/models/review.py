import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class Review(Base):
    """
    Review Queue entry created when a transaction is flagged for manual analyst review.
    """
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    evaluation_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("fraud_evaluations.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Status: PENDING, IN_REVIEW, APPROVED, REJECTED, ESCALATED
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", index=True)
    # Priority: LOW, MEDIUM, HIGH, CRITICAL
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM", index=True)

    assigned_analyst: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Analyst final manual decision: APPROVE, REJECT, ESCALATE
    decision: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    decision_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="reviews")
