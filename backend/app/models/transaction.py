import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.fraud_evaluation import FraudEvaluation
    from app.models.review import Review


class Transaction(Base):
    """
    Financial transaction entity model representing ingested payment events.
    """
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    merchant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    merchant_category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, default="WEB")
    
    # Device and Geolocation metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    location_city: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    location_country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Status: PENDING, APPROVED, REVIEW, REJECTED
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING", index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    evaluations: Mapped[List["FraudEvaluation"]] = relationship(
        "FraudEvaluation",
        back_populates="transaction",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review",
        back_populates="transaction",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_transactions_user_created", "user_id", "created_at"),
    )
