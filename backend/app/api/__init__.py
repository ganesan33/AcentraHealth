from fastapi import APIRouter
from app.api.v1 import (
    v1_router,
    transactions_router,
    fraud_router,
    reviews_router,
    dashboard_router,
    rules_router,
    graph_router,
)

# Root API router pointing directly to v1 versioned endpoints
api_router = v1_router

__all__ = [
    "api_router",
    "v1_router",
    "transactions_router",
    "fraud_router",
    "reviews_router",
    "dashboard_router",
    "rules_router",
    "graph_router",
]
