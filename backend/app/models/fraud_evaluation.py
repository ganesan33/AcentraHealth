import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict, TYPE_CHECKING
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.rule_result import RuleResultModel


class FraudEvaluation(Base):
    """
    Evaluation execution run recorded by the Fraud Engine for an ingested transaction.
    """
    __tablename__ = "fraud_evaluations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    final_decision: Mapped[str] = mapped_column(String(20), nullable=False)  # APPROVE, REVIEW, REJECT
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    triggered_rule_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evaluation_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="evaluations")
    rule_results: Mapped[List["RuleResultModel"]] = relationship(
        "RuleResultModel",
        back_populates="evaluation",
        cascade="all, delete-orphan",
    )
