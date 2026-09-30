from fastapi import APIRouter, status
from typing import Dict, Any

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", status_code=status.HTTP_200_OK)
async def list_transactions() -> Dict[str, Any]:
    """Placeholder endpoint for listing transactions."""
    return {"message": "List transactions endpoint placeholder", "data": []}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder endpoint for ingesting a transaction."""
    return {"message": "Transaction created successfully", "data": payload}
