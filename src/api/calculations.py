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


@router.get("/phase2/status")
def phase2_status():
    """Check Phase 2 integration status."""
    from src.modules.phase2_advanced import EnergyPlusIntegration, DaylightAdvanced, AdvancedShading, SensitivityAnalysis

    return {
        "energyplus": {
            "status": "not_implemented",
            "message": "EnergyPlus simulation requires Phase 2 integration with simulation server.",
            "available": False,
        },
        "daylight_advanced": {
            "status": "not_implemented",
            "message": "sDA/ASE calculation requires Radiance simulation (Phase 2).",
            "available": False,
        },
        "shading_analysis": {
            "status": "not_implemented",
            "message": "Advanced shading analysis requires 3D obstruction geometry (Phase 2).",
            "available": False,
        },
        "sensitivity": {
            "status": "not_implemented",
            "message": "Sensitivity analysis is planned for Phase 2.",
            "available": False,
        },
    }


@router.get("/phase3/status")
def phase3_status():
    """Check Phase 3 integration status."""
    from src.modules.phase3_bim import IFCImporter, BIMGeometryExtractor, GeometryValidator, IFCToAnalysisModel

    return {
        "ifc_import": {
            "status": "not_implemented",
            "message": "IFC file import requires IfcOpenShell integration (Phase 3).",
            "available": False,
        },
        "geometry_extraction": {
            "status": "not_implemented",
            "message": "BIM geometry extraction requires IfcOpenShell integration (Phase 3).",
            "available": False,
        },
        "geometry_validation": {
            "status": "not_implemented",
            "message": "Geometry validation requires Phase 3 implementation.",
            "available": False,
        },
        "ifc_conversion": {
            "status": "not_implemented",
            "message": "IFC-to-analysis conversion requires Phase 3 implementation.",
            "available": False,
        },
    }


@router.post("/phase2/energy-simulation")
def run_energy_simulation(request: dict):
    """Run EnergyPlus simulation (Phase 2 placeholder)."""
    from src.modules.phase2_advanced import EnergyPlusIntegration
    return EnergyPlusIntegration.run_energy_simulation(
        building_id=request.get("building_id", "preview"),
        rooms=request.get("rooms", []),
        epw_path=request.get("epw_path", "data/weather/Dhaka_419230.epw"),
    )


@router.post("/phase2/daylight-sda")
def calculate_sda(request: dict):
    """Calculate sDA/ASE (Phase 2 placeholder)."""
    from src.modules.phase2_advanced import DaylightAdvanced
    return DaylightAdvanced.calculate_sda(
        room_geometry=request.get("room_geometry", {}),
        epw_path=request.get("epw_path", "data/weather/Dhaka_419230.epw"),
        materials=request.get("materials", {}),
    )


@router.post("/phase3/import-ifc")
def import_ifc(request: dict):
    """Import IFC file (Phase 3 placeholder)."""
    from src.modules.phase3_bim import IFCImporter
    return IFCImporter.validate_file(request.get("file_path", ""))


@router.post("/phase3/extract-geometry")
def extract_bim_geometry(request: dict):
    """Extract BIM geometry from IFC (Phase 3 placeholder)."""
    from src.modules.phase3_bim import BIMGeometryExtractor
    return BIMGeometryExtractor.extract_building_elements(request.get("ifc_path", ""))