from fastapi import APIRouter
from backend.app.api.routes import (
    dashboard, forecast, inventory, risk, recommendations,
    models, research, audit, copilot, scenarios
)

api_router = APIRouter()
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(forecast.router, tags=["forecast"])
api_router.include_router(inventory.router, tags=["inventory"])
api_router.include_router(risk.router, tags=["risk"])
api_router.include_router(recommendations.router, tags=["recommendations"])
api_router.include_router(models.router, tags=["models"])
api_router.include_router(research.router, tags=["research"])
api_router.include_router(audit.router, tags=["audit"])
api_router.include_router(copilot.router, tags=["copilot"])
api_router.include_router(scenarios.router, tags=["scenarios"])
