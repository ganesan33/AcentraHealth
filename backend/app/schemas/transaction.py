from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    """Base schema attributes for a financial transaction."""
    user_id: str = Field(..., description="Unique customer/user identifier")
    account_id: str = Field(..., description="Source account identifier")
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="ISO-4217 Currency code")
    merchant_id: str = Field(..., description="Target merchant identifier")
    merchant_category: Optional[str] = Field(default=None, description="Merchant category or MCC code")
    channel: str = Field(default="WEB", description="Ingestion channel: WEB, MOBILE, POS, API")
    ip_address: Optional[str] = Field(default=None, description="IPv4 or IPv6 client address")
    device_id: Optional[str] = Field(default=None, description="Client fingerprint or device identifier")
    location_city: Optional[str] = Field(default=None, description="City location")
    location_country: Optional[str] = Field(default=None, max_length=2, description="2-letter ISO country code")
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0, description="Latitude coordinate")
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0, description="Longitude coordinate")


class TransactionCreate(TransactionBase):
    """Payload schema for ingesting a transaction into the engine."""
    id: Optional[str] = Field(default=None, description="Optional custom transaction ID; generated if omitted")


class TransactionRead(TransactionBase):
    """Response schema returning stored transaction details."""
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionFilter(BaseModel):
    """Query parameter schema for searching and filtering transactions."""
    user_id: Optional[str] = None
    account_id: Optional[str] = None
    status: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
