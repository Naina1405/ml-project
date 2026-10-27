"""
api/main.py
===========
FastAPI application entry-point for the Autonomous Personal Task Agent.

Endpoints
---------
GET  /          → Health-check / service info
POST /agent/run → Execute an agent goal (via agent router)
GET  /tasks     → List tasks (via tasks router)
GET  /memory    → List memories (via memory router)

SSE streaming events are available via /agent/run/stream (see agent router).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from db.crud import db_init

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan: initialise the database on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    logger.info("[API] Starting up — initialising database …")
    try:
        db_init()
        logger.info("[API] Database initialised successfully.")
    except Exception as exc:
        logger.error(f"[API] Database initialisation failed: {exc}")
    yield
    logger.info("[API] Shutting down.")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "REST + SSE backend for the Autonomous Personal Task Agent. "
        "Powered by LangGraph, ChromaDB, and FastAPI."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

from api.routers import agent, tasks, memory  # noqa: E402 (post-app definition)

app.include_router(agent.router, prefix="/agent", tags=["Agent"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(memory.router, prefix="/memory", tags=["Memory"])


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def health_check():
    """Returns service metadata and a health status."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
