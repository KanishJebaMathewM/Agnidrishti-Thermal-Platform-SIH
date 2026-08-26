from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import authorities, dashboard, events, feedback, health, model, notifications, sources

app = FastAPI(
    title="AGNIDRISHTI API",
    version="0.1.0",
    description="Thermal anomaly detection and monitoring platform",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(authorities.router, prefix="/authorities", tags=["authorities"])
app.include_router(feedback.router, tags=["feedback"])
app.include_router(notifications.router, tags=["notifications"])
app.include_router(model.router, prefix="/model", tags=["model"])
app.include_router(health.router, tags=["health"])