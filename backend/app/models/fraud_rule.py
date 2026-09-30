import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import String, Float, Boolean, DateTime, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class FraudRule(Base):
    """
    Persisted configuration for dynamic Fraud Detection Rules.
    Allows enabling/disabling, weight tuning, and parameter customization without redeployment.
    """
    __tablename__ = "fraud_rules"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False, default="GENERAL")
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Dynamic rule thresholds (e.g. {"max_frequency": 5, "window_seconds": 600})
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

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
