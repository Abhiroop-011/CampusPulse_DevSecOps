"""
CampusPulse FastAPI application entrypoint.

Wires up:
  - CORS middleware
  - Prometheus instrumentation on /metrics
  - All API routers (health, clubs, events, stats)
  - Startup seed data (only when explicitly enabled)
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api import health, clubs, events, stats
from app.core.config import settings

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger("campuspulse")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("CampusPulse starting up (environment=%s)", settings.environment)
    yield
    logger.info("CampusPulse shutting down")


app = FastAPI(
    title="CampusPulse API",
    description="Campus Events and Club Management Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Prometheus metrics — exposed at /metrics
# ---------------------------------------------------------------------------
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health.router)
app.include_router(clubs.router)
app.include_router(events.router)
app.include_router(stats.router)


@app.get("/", tags=["root"])
def root():
    return {
        "name": "CampusPulse API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "metrics": "/metrics",
    }
