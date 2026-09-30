from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate, TransactionRead

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=List[TransactionRead], status_code=status.HTTP_200_OK)
async def list_transactions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    account_id: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> List[TransactionRead]:
    """Retrieve filtered list of ingested transactions."""
    service = TransactionService(db)
    records = await service.list_transactions(
        limit=limit,
        offset=offset,
        status=status,
        user_id=user_id,
        account_id=account_id,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    return [TransactionRead.model_validate(tx) for tx in records]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Ingest a transaction and automatically evaluate it with the Fraud Engine."""
    service = TransactionService(db)
    result = await service.ingest_transaction(payload, evaluate=True)
    tx = result["transaction"]
    evaluation = result["evaluation"]

    return {
        "message": "Transaction ingested successfully",
        "transaction": TransactionRead.model_validate(tx),
        "evaluation": evaluation.model_dump() if evaluation else None,
    }


@router.get("/{transaction_id}", response_model=TransactionRead, status_code=status.HTTP_200_OK)
async def get_transaction_by_id(
    transaction_id: str,
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:
    """Fetch details for a specific transaction by ID."""
    service = TransactionService(db)
    tx = await service.get_transaction(transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID '{transaction_id}' was not found.",
        )
    return TransactionRead.model_validate(tx)
