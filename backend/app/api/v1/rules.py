from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.rules.registry import rule_registry
from app.repositories.rule_repository import RuleRepository
from app.models.fraud_rule import FraudRule
from app.schemas.rule import RuleCreate, RuleUpdate, RuleRead

router = APIRouter(prefix="/rules", tags=["Rule Management"])


@router.get("/", status_code=status.HTTP_200_OK)
async def list_rules(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List all registered and configured fraud rules."""
    repo = RuleRepository(db)
    db_rules = await repo.list_rules()
    active_engine_rules = rule_registry.get_all_rules()

    return {
        "engine_registered_rules": [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "description": r.description,
                "weight": r.weight,
                "enabled": r.enabled,
            }
            for r in active_engine_rules
        ],
        "database_rules": [
            RuleRead.model_validate(r) for r in db_rules
        ],
    }


@router.post("/", response_model=RuleRead, status_code=status.HTTP_201_CREATED)
async def create_rule(
    payload: RuleCreate,
    db: AsyncSession = Depends(get_db),
) -> RuleRead:
    """Create a new fraud rule configuration."""
    repo = RuleRepository(db)
    existing = await repo.get_by_code(payload.rule_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule with code '{payload.rule_code}' already exists.",
        )

    model = FraudRule(
        id=str(uuid.uuid4()),
        rule_code=payload.rule_code,
        name=payload.name,
        description=payload.description,
        rule_type=payload.rule_type,
        weight=payload.weight,
        is_active=payload.is_active,
        parameters=payload.parameters,
    )
    saved = await repo.create(model)
    return RuleRead.model_validate(saved)


@router.patch("/{rule_id}", response_model=RuleRead, status_code=status.HTTP_200_OK)
async def update_rule(
    rule_id: str,
    payload: RuleUpdate,
    db: AsyncSession = Depends(get_db),
) -> RuleRead:
    """Update rule weight, description, or activation status."""
    repo = RuleRepository(db)
    updated = await repo.update_rule(
        rule_id=rule_id,
        name=payload.name,
        description=payload.description,
        weight=payload.weight,
        is_active=payload.is_active,
        parameters=payload.parameters,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with ID '{rule_id}' was not found.",
        )
    return RuleRead.model_validate(updated)
