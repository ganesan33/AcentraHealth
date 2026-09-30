from typing import Dict, Any
from fastapi import APIRouter, Depends, status, HTTPException
from app.integrations.tigergraph.service import TigerGraphService, get_tigergraph_service
from app.integrations.tigergraph.exceptions import TigerGraphError
from app.core.logging import logger

router = APIRouter(prefix="/graph", tags=["Graph Operations (Development)"])


@router.post("/test-transaction", status_code=status.HTTP_201_CREATED)
async def test_transaction_graph_ingestion(
    payload: Dict[str, Any],
    tg_service: TigerGraphService = Depends(get_tigergraph_service),
) -> Dict[str, Any]:
    """
    [DEVELOPMENT / TEST ENDPOINT]
    Demonstrates graph ingestion: FastAPI -> TigerGraphService -> pyTigerGraph -> TigerGraph.
    Upserts User, Account, Transaction, Merchant, Device, Location, IP, and creates relationships.
    """
    try:
        # Supply defaults if minimal payload passed
        sample_data = {
            "transaction_id": payload.get("transaction_id", "tx_test_1001"),
            "user_id": payload.get("user_id", "usr_101"),
            "user_name": payload.get("user_name", "Jane Doe"),
            "account_id": payload.get("account_id", "acc_501"),
            "account_type": payload.get("account_type", "CHECKING"),
            "amount": payload.get("amount", 250.75),
            "currency": payload.get("currency", "USD"),
            "merchant_id": payload.get("merchant_id", "mer_808"),
            "merchant_name": payload.get("merchant_name", "Tech Superstore"),
            "device_id": payload.get("device_id", "dev_999"),
            "device_type": payload.get("device_type", "iOS"),
            "location_id": payload.get("location_id", "loc_77"),
            "city": payload.get("city", "New York"),
            "country": payload.get("country", "US"),
            "ip_address": payload.get("ip_address", "192.168.1.100"),
            "timestamp": payload.get("timestamp", "2026-09-30T12:00:00Z"),
        }

        success = tg_service.ingest_full_transaction(sample_data)
        return {
            "status": "success",
            "message": "Graph transaction ingestion executed successfully.",
            "data": sample_data,
        }

    except TigerGraphError as tg_err:
        logger.error(f"TigerGraph error during test transaction ingestion: {tg_err.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TigerGraph graph error: {tg_err.message}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in test-transaction endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during graph test ingestion.",
        )
