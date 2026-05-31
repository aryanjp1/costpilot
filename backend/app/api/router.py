from fastapi import APIRouter

from . import (
    alerts,
    analytics,
    api_keys,
    auth,
    budgets,
    events,
    ingest,
    members,
    projects,
    recommendations,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(members.router)
api_router.include_router(api_keys.router)
api_router.include_router(ingest.router)
api_router.include_router(analytics.router)
api_router.include_router(events.router)
api_router.include_router(budgets.router)
api_router.include_router(alerts.router)
api_router.include_router(recommendations.router)
