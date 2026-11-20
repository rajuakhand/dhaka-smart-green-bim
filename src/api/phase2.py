"""
Phase 2 API — Advanced analysis endpoints.

Exposes the physics-based advanced modules:
    - Climate (NASA POWER with BMD fallback)
    - Solar geometry (pvlib / NREL SPA)
    - Daylight factor (CIBSE/BRE)
    - Shading analysis
    - Sensitivity analysis
    - Parametric optimization
    - Material database
    - Simulation engine capability (honest)

NOTE: No endpoint here ever reports a simulated value. When EnergyPlus or
Radiance is unavailable, results are returned with status "Not evaluated".
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.api.projects import _projects
from src.api.rooms import _rooms
from src.models.schemas import BuildingCreate, RoomCreate
from src.modules import climate as climate_mod
from src.modules import daylight_factor as df_mod
from src.modules import materials as mat_mod
from src.modules import parametric as param_mod
from src.modules import sensitivity as sens_mod
from src.modules import shading as shade_mod
from src.modules import simulation_bridge
from src.modules import solar_geometry as solar_mod
from src.services.phase2_service import PHASE2_SOURCES, run_phase2_analysis

router = APIRouter(prefix="/phase2")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ClimateRequest(BaseModel):
    latitude: float = Field(default=solar_mod.DHAKA_LATITUDE, ge=-90, le=90)
    longitude: float = Field(default=solar_mod.DHAKA_LONGITUDE, ge=-180, le=180)
    start_year: int = Field(default=2005, ge=1980, le=2025)
    end_year: int = Field(default=2024, ge=1980, le=2025)


class SolarRequest(BaseModel):
    latitude: float = Field(default=solar_mod.DHAKA_LATITUDE, ge=-90, le=90)
    longitude: float = Field(default=solar_mod.DHAKA_LONGITUDE, ge=-180, le=180)
    orientation_deg: float = Field(default=180.0, ge=0, le=360)
    date: str = Field(default="2026-06-21")


class DaylightRequest(BaseModel):
    window_area_m2: float = Field(gt=0)
    window_width_m: float = Field(gt=0)
    window_height_m: float = Field(gt=0)
    room_length_m: float = Field(gt=0)
    room_width_m: float = Field(gt=0)
    room_height_m: float = Field(gt=0)
    glazing_type: str = Field(default="Clear")
    obstruction_height_m: float = Field(default=0.0, ge=0)
    obstruction_distance_m: float = Field(default=0.0, ge=0)


class ShadingRequest(BaseModel):
    latitude: float = Field(default=solar_mod.DHAKA_LATITUDE, ge=-90, le=90)
    longitude: float = Field(default=solar_mod.DHAKA_LONGITUDE, ge=-180, le=180)
    facade_azimuth_deg: float = Field(default=180.0, ge=0, le=360)
    window_height_m: float = Field(default=1.5, gt=0)
    window_width_m: float = Field(default=2.0, gt=0)
    overhang_depth_m: float = Field(default=0.0, ge=0)
    fin_depth_m: float = Field(default=0.0, ge=0)
    date: str = Field(default="2026-06-21")
    obstruction_height_m: float = Field(default=0.0, ge=0)
    obstruction_distance_m: float = Field(default=0.0, ge=0)


class EnvelopeRequest(BaseModel):
    wall_assembly_id: str = Field(default="WALL-BRICK-150")
    roof_assembly_id: str = Field(default="ROOF-CONCRETE-125")
    glazing_type: str = Field(default="Clear")
    wall_area_m2: float = Field(default=0.0, ge=0)
    roof_area_m2: float = Field(default=0.0, ge=0)
    glazing_area_m2: float = Field(default=0.0, ge=0)


# ---------------------------------------------------------------------------
# Simulation capability (honest)
# ---------------------------------------------------------------------------

@router.get("/simulation-capability")
def simulation_capability():
    """Report whether external simulation engines are available.

    This never claims a simulation ran. Use it to decide whether to show
    "Simulated" or "Not evaluated" in the UI.
    """
    return simulation_bridge.simulation_capability_report()


# ---------------------------------------------------------------------------
# Climate
# ---------------------------------------------------------------------------

@router.get("/climate")
def get_climate(
    latitude: float = solar_mod.DHAKA_LATITUDE,
    longitude: float = solar_mod.DHAKA_LONGITUDE,
    start_year: int = 2005,
    end_year: int = 2024,
):
    """Fetch climate normals (NASA POWER with cached + BMD fallback)."""
    try:
        dataset = climate_mod.fetch_nasa_power(
            latitude, longitude, start_year, end_year
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Climate data unavailable: {exc}")

    return {
        "dataset": climate_mod.climate_summary(dataset),
        "cooling_degree_days": climate_mod.cooling_degree_days(dataset, 26.0),
        "parameters": {
            name: {"description": desc, "unit": unit}
            for name, (desc, unit) in climate_mod.NASA_POWER_PARAMETERS.items()
        },
        "engineering_note": climate_mod.NASA_POWER_UNITS_NOTE,
    }


# ---------------------------------------------------------------------------
# Solar geometry
# ---------------------------------------------------------------------------

@router.post("/solar")
def solar_analysis(req: SolarRequest):
    """Solar geometry for a location, date and building orientation."""
    import pandas as pd

    try:
        date = pd.Timestamp(req.date)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format; use YYYY-MM-DD")

    return {
        "sun_path": solar_mod.daily_sun_path(req.latitude, req.longitude, date),
        "facade_solar": solar_mod.facade_solar_summary(
            req.latitude, req.longitude, req.orientation_deg, date
        ),
        "shgc_table": solar_mod.DEFAULT_SHGC,
    }


@router.post("/solar/heat-gain")
def solar_heat_gain(req: dict):
    """Instantaneous solar heat gain through glazing.

    Q = A x I x SHGC x shading_factor
    """
    from src.core.exceptions import ValidationFailure

    try:
        return solar_mod.solar_heat_gain(
            glass_area_m2=float(req.get("glass_area_m2", 0.0)),
            incident_irradiance_w_m2=float(req.get("incident_irradiance_w_m2", 0.0)),
            shgc=float(req.get("shgc", 0.82)),
            shading_factor=float(req.get("shading_factor", 1.0)),
        )
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except ValidationFailure as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ---------------------------------------------------------------------------
# Daylight factor
# ---------------------------------------------------------------------------

@router.post("/daylight")
def daylight_factor(req: DaylightRequest):
    """CIBSE/BRE average daylight factor for a room."""
    from src.core.exceptions import ValidationFailure

    try:
        df = df_mod.average_daylight_factor(
            window_area_m2=req.window_area_m2,
            window_width_m=req.window_width_m,
            window_height_m=req.window_height_m,
            room_length_m=req.room_length_m,
            room_width_m=req.room_width_m,
            room_height_m=req.room_height_m,
            glazing_type=req.glazing_type,
            obstruction_height_m=req.obstruction_height_m,
            obstruction_distance_m=req.obstruction_distance_m,
        )
    except ValidationFailure as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "daylight_factor": df,
        "indicative_lux": df_mod.df_to_lux_estimate(df["daylight_factor_percent"]),
    }


@router.get("/daylight/glazing")
def daylight_glazing_table():
    """Glazing diffuse transmittance reference values."""
    return {
        "transmittance": df_mod.GLAZING_TRANSMITTANCE,
        "maintenance_factor": df_mod.DEFAULT_MAINTENANCE_FACTOR,
        "default_reflectance": df_mod.DEFAULT_REFLECTANCE,
        "note": (
            "Screening defaults. Substitute manufacturer data when available. "
            "Values are not Bangladesh-specific measurements."
        ),
    }


# ---------------------------------------------------------------------------
# Shading
# ---------------------------------------------------------------------------

@router.post("/shading")
def shading_analysis(req: ShadingRequest):
    """Geometric shading analysis for a facade."""
    import pandas as pd

    from src.core.exceptions import ValidationFailure

    try:
        return shade_mod.facade_shading_analysis(
            latitude=req.latitude,
            longitude=req.longitude,
            facade_azimuth_deg=req.facade_azimuth_deg,
            window_height_m=req.window_height_m,
            window_width_m=req.window_width_m,
            overhang_depth_m=req.overhang_depth_m,
            fin_depth_m=req.fin_depth_m,
            date=pd.Timestamp(req.date),
            obstruction_distance_m=req.obstruction_distance_m,
            obstruction_height_m=req.obstruction_height_m,
        )
    except ValidationFailure as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format; use YYYY-MM-DD")


# ---------------------------------------------------------------------------
# Sensitivity
# ---------------------------------------------------------------------------

@router.post("/sensitivity")
def sensitivity_analysis(req: dict):
    """One-at-a-time sensitivity analysis.

    Because the metric function is defined in Python, this endpoint runs the
    sensitivity analysis against the built-in preliminary energy estimator and
    accepts overrides for its four schedule/assumption parameters.
    """
    from src.modules.energy import estimate_building_energy

    base = {
        "ac_cop": float(req.get("ac_cop", 3.1)),
        "cooling_hours": float(req.get("cooling_hours", 1800.0)),
        "lighting_hours": float(req.get("lighting_hours", 2500.0)),
        "equipment_hours": float(req.get("equipment_hours", 2500.0)),
    }
    delta = float(req.get("delta", 0.10))
    project_id = req.get("project_id")

    if project_id:
        if project_id not in _projects:
            raise HTTPException(status_code=404, detail="Project not found.")
        rooms = _rooms.get(project_id, [])
    else:
        rooms = [
            RoomCreate(
                name="Default Room", room_type="Residential",
                length_m=float(req.get("length_m", 5.0)),
                width_m=float(req.get("width_m", 4.0)),
                height_m=float(req.get("height_m", 3.0)),
                occupants=2,
                window_area_m2=4.0,
                openable_window_area_m2=2.0,
            )
        ]

    if not rooms:
        raise HTTPException(status_code=400, detail="No rooms available for analysis.")

    def _metric(d: dict) -> float:
        return estimate_building_energy(
            rooms,
            ac_cop=d["ac_cop"],
            cooling_hours=d["cooling_hours"],
            lighting_hours=d["lighting_hours"],
            equipment_hours=d["equipment_hours"],
        )["total_electricity_kwh_per_year"]

    from src.core.exceptions import ValidationFailure

    try:
        return sens_mod.one_at_a_time_sensitivity(
            baseline_inputs=base, metric_function=_metric, delta=delta
        )
    except ValidationFailure as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# ---------------------------------------------------------------------------
# Materials / envelope
# ---------------------------------------------------------------------------

@router.get("/materials")
def material_database():
    """Local material and assembly database with U-values."""
    return mat_mod.list_assemblies()


@router.post("/envelope")
def envelope_analysis(req: EnvelopeRequest):
    """Envelope summary and area-weighted U-value."""
    return mat_mod.envelope_summary(
        wall_assembly_id=req.wall_assembly_id,
        roof_assembly_id=req.roof_assembly_id,
        glazing_type=req.glazing_type,
        wall_area_m2=req.wall_area_m2,
        roof_area_m2=req.roof_area_m2,
        glazing_area_m2=req.glazing_area_m2,
    )


# ---------------------------------------------------------------------------
# Full Phase 2 run
# ---------------------------------------------------------------------------

@router.post("/projects/{project_id}/run")
def run_phase2(project_id: str):
    """Run the full Phase 2 advanced analysis for a project."""
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found.")

    rooms = _rooms.get(project_id, [])
    if not rooms:
        raise HTTPException(status_code=400, detail="No rooms defined for this project.")

    try:
        return run_phase2_analysis(_projects[project_id], rooms)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Phase 2 analysis failed: {exc}")


@router.post("/preview")
def run_phase2_preview(building: BuildingCreate, rooms: list[RoomCreate], design_date: str = "2026-06-21"):
    """Run Phase 2 analysis without persisting a project."""
    try:
        return run_phase2_analysis(building, rooms, design_date=design_date)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Phase 2 analysis failed: {exc}")


@router.get("/sources")
def phase2_sources():
    """Source references used by Phase 2."""
    return {"sources": PHASE2_SOURCES}