from fastapi import APIRouter
from app.api.transactions import router as transactions_router
from app.api.fraud import router as fraud_router
from app.api.reviews import router as reviews_router
from app.api.dashboard import router as dashboard_router
from app.api.rules import router as rules_router
from app.api.graph import router as graph_router
from app.api.investigation import router as investigation_router

api_router = APIRouter()
api_router.include_router(transactions_router)
api_router.include_router(fraud_router)
api_router.include_router(reviews_router)
api_router.include_router(dashboard_router)
api_router.include_router(rules_router)
api_router.include_router(graph_router)
api_router.include_router(investigation_router)

__all__ = [
    "api_router",
    "transactions_router",
    "fraud_router",
    "reviews_router",
    "dashboard_router",
    "rules_router",
    "graph_router",
    "investigation_router",
]
