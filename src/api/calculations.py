"""
Calculations API — endpoints for running the deterministic calculation engine.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.projects import _projects
from src.api.rooms import _rooms
from src.models.schemas import BuildingCreate, RoomCreate, CalculationEnvelope
from src.services.calculation_service import run_full_analysis

router = APIRouter()


class CalculationRequest(BaseModel):
    """Request body for running calculations."""

    ac_cop: float = 3.1
    cooling_hours: float = 1800.0
    lighting_hours: float = 2500.0
    equipment_hours: float = 2500.0
    emission_factor_source: str = "DoE-GEF"
    rajuk_zone: str | None = None
    alternatives: list[dict] | None = None


@router.post("/projects/{project_id}/calculate", response_model=CalculationEnvelope)
def calculate_project(project_id: str, request: CalculationRequest | None = None):
    """Run all calculation modules for a project.

    Returns the full result envelope with confidence, sources, and limitations.
    """
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found.")

    project = _projects[project_id]
    rooms = _rooms.get(project_id, [])

    if not rooms:
        raise HTTPException(
            status_code=400,
            detail="No rooms defined for this project. Add rooms first.",
        )

    req = request or CalculationRequest()

    try:
        result = run_full_analysis(
            building=project,
            rooms=rooms,
            ac_cop=req.ac_cop,
            cooling_hours=req.cooling_hours,
            lighting_hours=req.lighting_hours,
            equipment_hours=req.equipment_hours,
            emission_factor_source=req.emission_factor_source,
            rajuk_zone=req.rajuk_zone,
            alternatives=req.alternatives,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


@router.post("/calculate/preview", response_model=CalculationEnvelope)
def calculate_preview(
    building: BuildingCreate,
    rooms: list[RoomCreate],
    request: CalculationRequest | None = None,
):
    """Run a calculation preview without saving to a project.

    Useful for testing and prototyping.
    """
    req = request or CalculationRequest()

    try:
        result = run_full_analysis(
            building=building,
            rooms=rooms,
            ac_cop=req.ac_cop,
            cooling_hours=req.cooling_hours,
            lighting_hours=req.lighting_hours,
            equipment_hours=req.equipment_hours,
            emission_factor_source=req.emission_factor_source,
            rajuk_zone=req.rajuk_zone,
            alternatives=req.alternatives,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")