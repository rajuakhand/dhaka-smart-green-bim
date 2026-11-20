"""
Phase 2 — Advanced Analysis Orchestration.

Runs the physics-based advanced modules (climate, solar geometry, daylight
factor, shading, sensitivity, parametric optimization, materials) and reports
external simulation engines honestly.

Every result carries:
    - method (the formula/model used)
    - status (Calculated / Estimated / Not evaluated)
    - confidence
    - limitations
    - source references
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pandas as pd

from src.core.exceptions import ValidationFailure
from src.models.schemas import (
    BuildingCreate,
    ConfidenceLevel,
    RoomCreate,
    ResultStatus,
)
from src.modules import climate as climate_mod
from src.modules import daylight_factor as df_mod
from src.modules import materials as mat_mod
from src.modules import parametric as param_mod
from src.modules import sensitivity as sens_mod
from src.modules import shading as shade_mod
from src.modules import simulation_bridge
from src.modules import solar_geometry as solar_mod

PHASE2_SOURCES = [
    "SRC-011: NASA POWER (monthly climate normals, 0.5 deg)",
    "SRC-020: BMD 1991-2020 Dhaka climate normals (fallback)",
    "SRC-001: BNBC 2020 Part 3 Ch 4 (Energy Efficiency & Sustainability)",
    "SRC-016: HBRI / BNBC Part 5 materials context",
    "CIBSE/SLL LG10: average daylight factor method",
    "ISO 6946: building components and elements - thermal transmittance",
    "NREL SPA: Reda & Andreas (2004) solar position algorithm",
]

PHASE2_DISCLAIMER = (
    "Phase 2 results are PHYSICS-BASED CALCULATIONS (solar geometry, daylight "
    "factor, shading) and ESTIMATES from verified data sources. They are NOT "
    "hourly building energy simulation and NOT climate-based daylight "
    "simulation. Where EnergyPlus or Radiance is unavailable, those results are "
    "reported as 'Not evaluated' — never as simulated."
)


def run_phase2_analysis(
    building: BuildingCreate,
    rooms: list[RoomCreate],
    *,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    design_date: str = "2026-06-21",
    ac_cop: float = 3.1,
    cooling_hours: float = 1800.0,
    lighting_hours: float = 2500.0,
    equipment_hours: float = 2500.0,
    alternatives: Optional[list[dict]] = None,
) -> dict:
    """Run the full Phase 2 advanced analysis suite."""

    lat = latitude if latitude is not None else solar_mod.DHAKA_LATITUDE
    lon = longitude if longitude is not None else solar_mod.DHAKA_LONGITUDE
    date = pd.Timestamp(design_date)

    # --- Climate ---
    climate = climate_mod.fetch_nasa_power(lat, lon, 2005, 2024)
    climate_summary = climate_mod.climate_summary(climate)
    cdd = climate_mod.cooling_degree_days(climate, base_c=26.0)

    # --- Solar geometry ---
    sun_path = solar_mod.daily_sun_path(lat, lon, date)
    orientation = getattr(building, "orientation_deg", None) or 0.0
    facade_solar = solar_mod.facade_solar_summary(lat, lon, orientation, date)

    # --- Solar heat gain for the most exposed room window ---
    worst_facade = facade_solar["facades"][facade_solar["highest_exposure_facade"]]
    sample_room = rooms[0] if rooms else None
    if sample_room is not None:
        shgc = solar_mod.shgc_for_glazing(
            sample_room.glazing_type.value if sample_room.glazing_type else "Clear"
        )
        heat_gain = solar_mod.solar_heat_gain(
            glass_area_m2=sample_room.window_area_m2,
            incident_irradiance_w_m2=worst_facade["peak_poa_w_m2"],
            shgc=shgc,
        )
    else:
        heat_gain = {"status": ResultStatus.INSUFFICIENT_DATA.value,
                     "message": "No rooms defined."}

    # --- Daylight factor per room ---
    daylight_results = []
    for room in rooms:
        try:
            df = df_mod.average_daylight_factor(
                window_area_m2=max(room.window_area_m2, 0.001),
                window_width_m=max(room.length_m * 0.4, 0.5),
                window_height_m=max(room.height_m * 0.5, 0.5),
                room_length_m=room.length_m,
                room_width_m=room.width_m,
                room_height_m=room.height_m,
                glazing_type=(
                    room.glazing_type.value if room.glazing_type else "Clear"
                ),
                obstruction_height_m=room.external_obstruction_height_m,
            )
            daylight_results.append({
                "room_name": room.name,
                **df,
                "indicative_lux": df_mod.df_to_lux_estimate(
                    df["daylight_factor_percent"]
                )["indicative_interior_illuminance_lux"],
            })
        except ValidationFailure as exc:
            daylight_results.append({
                "room_name": room.name,
                "status": ResultStatus.INSUFFICIENT_DATA.value,
                "message": str(exc),
            })

    # --- Shading analysis on the main facade ---
    shading = shade_mod.facade_shading_analysis(
        latitude=lat,
        longitude=lon,
        facade_azimuth_deg=orientation,
        window_height_m=(rooms[0].height_m * 0.5) if rooms else 1.5,
        window_width_m=(rooms[0].length_m * 0.4) if rooms else 2.0,
        date=date,
    )

    # --- Material / envelope summary ---
    total_floor_area = sum(r.floor_area_m2 for r in rooms)
    wall_area = sum(r.wall_area_m2 for r in rooms) * 0.5  # ~half are exterior
    roof_area = rooms[0].floor_area_m2 if rooms else 0.0
    glass_area = sum(r.window_area_m2 for r in rooms)
    envelope = mat_mod.envelope_summary(
        wall_area_m2=wall_area,
        roof_area_m2=roof_area,
        glazing_area_m2=glass_area,
    )
    materials = mat_mod.list_assemblies()

    # --- Sensitivity analysis ---
    def _energy_metric(d: dict) -> float:
        from src.modules.energy import estimate_building_energy
        return estimate_building_energy(
            rooms,
            ac_cop=d["ac_cop"],
            cooling_hours=d["cooling_hours"],
            lighting_hours=d["lighting_hours"],
            equipment_hours=d["equipment_hours"],
        )["total_electricity_kwh_per_year"]

    sensitivity = sens_mod.one_at_a_time_sensitivity(
        baseline_inputs={
            "ac_cop": ac_cop,
            "cooling_hours": cooling_hours,
            "lighting_hours": lighting_hours,
            "equipment_hours": equipment_hours,
        },
        metric_function=_energy_metric,
        delta=0.10,
    )

    # --- Parametric optimization ---
    def _epi(design: dict) -> float:
        from src.modules.energy import estimate_building_energy
        return estimate_building_energy(
            rooms,
            ac_cop=design["ac_cop"],
            cooling_hours=design["cooling_hours"],
            lighting_hours=design["lighting_hours"],
            equipment_hours=design["equipment_hours"],
        )["energy_performance_index_kwh_m2"]

    design_space = {
        "ac_cop": [2.8, 3.1, 3.5, 4.0],
        "cooling_hours": [1200, 1500, 1800, 2100],
        "lighting_hours": [2000, 2500, 3000],
        "equipment_hours": [2000, 2500, 3000],
    }
    optimization = param_mod.grid_search(
        design_space=design_space,
        objective_function=_epi,
        maximise=False,
    )

    # --- Simulation engine status (honest) ---
    engines = simulation_bridge.simulation_capability_report()

    # --- Assemble ---
    module_results = {
        "climate": {
            "dataset": climate_summary,
            "cooling_degree_days": cdd,
            "status": ResultStatus.VERIFIED.value if climate.dataset_id == "SRC-011"
            else ResultStatus.ESTIMATED.value,
            "confidence": ConfidenceLevel.HIGH.value,
        },
        "solar_geometry": {
            "sun_path": sun_path,
            "facade_solar": facade_solar,
            "solar_heat_gain": heat_gain,
            "status": ResultStatus.ESTIMATED.value,
            "confidence": ConfidenceLevel.MEDIUM.value,
            "method": "NREL SPA + Ineichen-Perez clear-sky (pvlib)",
        },
        "daylight_factor": {
            "rooms": daylight_results,
            "method": "CIBSE/SLL LG10 average daylight factor",
            "status": ResultStatus.ESTIMATED.value,
            "confidence": ConfidenceLevel.MEDIUM.value,
        },
        "shading": shading,
        "materials": materials,
        "envelope": envelope,
        "sensitivity": sensitivity,
        "optimization": optimization,
        "simulation_engines": engines,
    }

    confidences = [
        module_results["climate"]["confidence"],
        module_results["solar_geometry"]["confidence"],
        module_results["daylight_factor"]["confidence"],
        shading["confidence"],
        envelope.get("status") == "Estimated" and ConfidenceLevel.MEDIUM.value
        or ConfidenceLevel.INSUFFICIENT.value,
    ]
    if any("High" in c for c in confidences) and not any("Insufficient" in c for c in confidences):
        overall = ConfidenceLevel.MEDIUM.value
    else:
        overall = ConfidenceLevel.LOW.value

    return {
        "phase": "Phase 2 - Advanced Analysis",
        "calculated_at": datetime.now(timezone.utc).isoformat(),
        "location": {"latitude": lat, "longitude": lon, "design_date": design_date},
        "modules": module_results,
        "source_references": PHASE2_SOURCES,
        "overall_confidence": overall,
        "disclaimer": PHASE2_DISCLAIMER,
        "simulation_status": {
            "energyplus_executed": False,
            "radiance_executed": False,
            "note": (
                "No external simulation engine was executed for this analysis. "
                "Values are analytical calculations or estimates."
            ),
        },
    }