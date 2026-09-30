from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class RuleBase(BaseModel):
    """Base schema for rule configuration."""
    rule_code: str = Field(..., description="Unique alphanumeric identifier (e.g. VELOCITY_1H)")
    name: str = Field(..., description="Human-readable rule name")
    description: Optional[str] = Field(default=None, description="Detailed explanation of rule logic")
    rule_type: str = Field(default="GENERAL", description="Rule category: VELOCITY, AMOUNT, LOCATION, etc.")
    weight: float = Field(default=10.0, ge=0.0, le=100.0, description="Risk score impact when triggered")
    is_active: bool = Field(default=True, description="Whether this rule executes during fraud evaluation")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Dynamic thresholds and configuration parameters")


class RuleCreate(RuleBase):
    """Schema for creating a new fraud rule."""
    pass


class RuleUpdate(BaseModel):
    """Schema for updating an existing rule configuration."""
    name: Optional[str] = None
    description: Optional[str] = None
    weight: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    is_active: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None


class RuleRead(RuleBase):
    """Schema for reading a rule configuration."""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
