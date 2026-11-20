"""
DhakaSmart Urban Density & Green BIM — FastAPI Application.

Provides REST API endpoints for:
- Building / Room CRUD
- Calculation orchestration
- Report generation
- Data source lookup
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api import projects, rooms, calculations, reports, phase2
from src.core.config import settings

app = FastAPI(
    title="DhakaSmart Urban Density & Green BIM",
    description=(
        "Bangladesh Climate-Aware Building Performance & Space Optimization Platform. "
        "Preliminary, evidence-driven building analysis for Dhaka's dense urban environment."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://rajuakhand.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router, prefix=settings.api_prefix, tags=["Projects"])
app.include_router(rooms.router, prefix=settings.api_prefix, tags=["Rooms"])
app.include_router(calculations.router, prefix=settings.api_prefix, tags=["Calculations"])
app.include_router(reports.router, prefix=settings.api_prefix, tags=["Reports"])
app.include_router(phase2.router, prefix=settings.api_prefix, tags=["Phase 2 — Advanced Analysis"])


@app.get("/", tags=["Health"])
def root():
    """Root endpoint with platform info."""
    return {
        "name": "DhakaSmart Urban Density & Green BIM",
        "version": "0.1.0",
        "description": "Bangladesh Climate-Aware Building Performance Platform",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


@app.get("/api/v1/health", tags=["Health"])
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/v1/sources", tags=["Data Sources"])
def list_sources():
    """List verified data sources from the source registry."""
    import csv
    from pathlib import Path

    registry_path = Path(settings.epw_dir).parent / "source_registry.csv"
    if not registry_path.exists():
        return {"sources": [], "note": "Source registry not found."}

    sources = []
    with open(registry_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sources.append(dict(row))

    return {"sources": sources, "count": len(sources)}