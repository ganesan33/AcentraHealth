from fastapi import APIRouter, status
from typing import Dict, Any

router = APIRouter(prefix="/rules", tags=["Rule Management"])


@router.get("/", status_code=status.HTTP_200_OK)
async def list_rules() -> Dict[str, Any]:
    """Placeholder endpoint to list registered fraud rules."""
    return {"message": "List rules placeholder", "rules": []}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rule(rule_config: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder endpoint to create or register a new fraud rule configuration."""
    return {"message": "Rule created placeholder", "rule": rule_config}
