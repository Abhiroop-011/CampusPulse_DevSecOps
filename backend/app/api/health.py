"""
Health and readiness probe endpoints.
"""
from fastapi import APIRouter

from app.core.database import check_db_connection
from app.schemas.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
def health():
    """Returns 200 OK when the application process is alive."""
    return {"status": "healthy"}


@router.get("/ready", response_model=ReadyResponse, summary="Readiness probe")
def ready():
    """Returns 200 OK only when the application can reach the database."""
    if check_db_connection():
        return {"status": "ready", "database": "connected"}
    return ReadyResponse(status="not_ready", database="unreachable")
