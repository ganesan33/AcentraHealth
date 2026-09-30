from fastapi import APIRouter
from app.api.v1.transactions import router as transactions_router
from app.api.v1.fraud import router as fraud_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.rules import router as rules_router
from app.api.graph import router as graph_router
from app.api.investigation import router as investigation_router

v1_router = APIRouter()
v1_router.include_router(transactions_router)
v1_router.include_router(fraud_router)
v1_router.include_router(reviews_router)
v1_router.include_router(dashboard_router)
v1_router.include_router(rules_router)
v1_router.include_router(graph_router)
v1_router.include_router(investigation_router)

__all__ = [
    "v1_router",
    "transactions_router",
    "fraud_router",
    "reviews_router",
    "dashboard_router",
    "rules_router",
    "graph_router",
    "investigation_router",
]
