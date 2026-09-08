"""EdgeHealth Guardian Network - FastAPI backend entrypoint.

This backend mirrors a subset of edge-hub state for the caregiver
dashboard. It is NOT where raw biometric inference happens - that
runs on the edge hub. This service handles auth, dashboard reads,
alert acknowledgment, and (optionally) mirrored predictions when a
device chooses to sync.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    health_data,
    predictions,
    alerts,
    digital_twin,
    chat,
    simulation
)

app = FastAPI(
    title="EdgeHealth Guardian Network API",
    description="Caregiver-facing API mirroring edge-hub health intelligence.",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(
    health_data.router,
    prefix="/health-data",
    tags=["health-data"]
)

app.include_router(
    predictions.router,
    prefix="/prediction",
    tags=["predictions"]
)

app.include_router(
    alerts.router,
    prefix="/alerts",
    tags=["alerts"]
)

app.include_router(
    digital_twin.router,
    prefix="/digital-twin",
    tags=["digital-twin"]
)

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

# Simulation Route
app.include_router(
    simulation.router,
    prefix="/simulation",
    tags=["simulation"]
)

# Home Route
@app.get("/")
def home():
    return {
        "status": "success",
        "message": "EdgeHealth Guardian Backend Running Successfully 🚀"
    }

# Health Check
@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }