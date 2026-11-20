"""
Module E — Preliminary Energy Estimator.

Computes a preliminary (screening-level) annual electricity estimate for
cooling, lighting, and equipment. This is NOT a simulation.

The preliminary estimate uses:
- SREDA AC Energy Efficiency Benchmark 2021 (COP by AC type)
- BNBC lighting power density references
- World Bank BEEER survey baseline (residential EPI ~42 kWh/m²/yr)
- User-supplied schedules and assumptions

IMPORTANT: This module never claims verified energy performance. The result
is always labelled "preliminary" with confidence level.

Formula summary:
  Cooling   = (AC capacity W/m² × floor area × cooling hours) / COP / 1000  [kWh]
  Lighting  = (lighting density W/m² × floor area × lighting hours) / 1000  [kWh]
  Equipment = (equipment density W/m² × floor area × equipment hours) / 1000  [kWh]
  Total     = Cooling + Lighting + Equipment + Other
  EPI       = Total kWh / Total floor area  [kWh/m²/yr]
"""
from __future__ import annotations

from src.models.schemas import RoomCreate, ConfidenceLevel, ResultStatus

# SREDA AC Benchmark 2021: Average COP for split AC in Bangladesh
# Source: SREDA "Air Conditioner Energy Efficiency Benchmark 2021"
SREDA_AC_BENCHMARK_COP = {
    "Split 1-2 TON": 3.146,
    "Split 2-4.5 TON": 2.9,
    "Multi-Split/VRF >4.5 TON": 3.67,
    "Default": 3.1,
}

# BNBC reference lighting power density (W/m²)
# These are representative values for preliminary screening.
BNBC_LIGHTING_DENSITY_W_M2 = {
    "Residential": 7.0,
    "Office": 9.0,
    "Classroom": 10.0,
    "Hospital": 12.0,
    "Retail": 15.0,
    "Storage": 5.0,
    "Laboratory": 15.0,
    "Assembly": 8.0,
    "Other": 7.0,
}

# Typical equipment/plug load (W/m²)
EQUIPMENT_DENSITY_W_M2 = {
    "Residential": 5.0,
    "Office": 10.0,
    "Classroom": 5.0,
    "Hospital": 15.0,
    "Retail": 8.0,
    "Storage": 3.0,
    "Laboratory": 20.0,
    "Assembly": 5.0,
    "Other": 5.0,
}

# Typical AC cooling capacity per m² (W/m²)
# Rule of thumb: ~60-80 W/m² for residential in hot-humid climate
AC_CAPACITY_W_M2 = {
    "Residential": 60.0,
    "Office": 80.0,
    "Classroom": 80.0,
    "Hospital": 80.0,
    "Retail": 80.0,
    "Storage": 40.0,
    "Laboratory": 80.0,
    "Assembly": 60.0,
    "Other": 60.0,
}


def estimate_room_energy(
    room: RoomCreate,
    ac_cop: float = 3.1,
    cooling_hours: float = 1800.0,
    lighting_hours: float = 2500.0,
    equipment_hours: float = 2500.0,
    ac_capacity_override: float | None = None,
    lighting_override: float | None = None,
    equipment_override: float | None = None,
) -> dict:
    """Estimate preliminary annual electricity for a single room.

    Returns cooling, lighting, equipment kWh and the sum.
    """
    floor_area = room.floor_area_m2

    # Resolve defaults from building type
    ac_capacity = ac_capacity_override or AC_CAPACITY_W_M2.get(room.room_type.value, 60.0)
    lighting_density = lighting_override or BNBC_LIGHTING_DENSITY_W_M2.get(room.room_type.value, 7.0)
    equipment_density = equipment_override or EQUIPMENT_DENSITY_W_M2.get(room.room_type.value, 5.0)

    # Cooling: (W/m² × m² × hours) / COP / 1000 → kWh
    cooling_kwh = (ac_capacity * floor_area * cooling_hours) / (ac_cop * 1000.0)

    # Lighting: (W/m² × m² × hours) / 1000 → kWh
    lighting_kwh = (lighting_density * floor_area * lighting_hours) / 1000.0

    # Equipment: (W/m² × m² × hours) / 1000 → kWh
    equipment_kwh = (equipment_density * floor_area * equipment_hours) / 1000.0

    total = cooling_kwh + lighting_kwh + equipment_kwh

    return {
        "room_id": getattr(room, "id", None),
        "room_name": room.name,
        "room_type": room.room_type.value,
        "floor_area_m2": floor_area,
        "cooling_kwh": round(cooling_kwh, 2),
        "lighting_kwh": round(lighting_kwh, 2),
        "equipment_kwh": round(equipment_kwh, 2),
        "total_kwh": round(total, 2),
    }


def estimate_building_energy(
    rooms: list[RoomCreate],
    ac_cop: float = 3.1,
    cooling_hours: float = 1800.0,
    lighting_hours: float = 2500.0,
    equipment_hours: float = 2500.0,
    building_type: str | None = None,
) -> dict:
    """Estimate preliminary annual electricity for a whole building.

    Aggregates per-room estimates and computes EPI.
    """
    results = [
        estimate_room_energy(
            room,
            ac_cop=ac_cop,
            cooling_hours=cooling_hours,
            lighting_hours=lighting_hours,
            equipment_hours=equipment_hours,
        )
        for room in rooms
    ]

    total_cooling = sum(r["cooling_kwh"] for r in results)
    total_lighting = sum(r["lighting_kwh"] for r in results)
    total_equipment = sum(r["equipment_kwh"] for r in results)
    total_kwh = sum(r["total_kwh"] for r in results)
    total_floor_area = sum(r["floor_area_m2"] for r in results)

    epi = round(total_kwh / total_floor_area, 2) if total_floor_area > 0 else 0.0

    # Confidence assessment
    # Higher confidence if we have many rooms and reasonable inputs.
    if len(results) >= 10:
        confidence = ConfidenceLevel.MEDIUM.value
    else:
        confidence = ConfidenceLevel.LOW.value

    limitations = [
        "Preliminary estimate only; no hourly simulation.",
        "Cooling estimate uses rule-of-thumb W/m², not a cooling load calculation.",
        "Lighting/equipment densities are screening defaults, not metered values.",
        "Weather effects (solar gain, humidity) are not explicitly modelled.",
    ]

    return {
        "mode": "preliminary",
        "rooms": results,
        "breakdown": {
            "cooling_kwh": round(total_cooling, 2),
            "lighting_kwh": round(total_lighting, 2),
            "equipment_kwh": round(total_equipment, 2),
            "total_kwh": round(total_kwh, 2),
        },
        "total_electricity_kwh_per_year": round(total_kwh, 2),
        "total_floor_area_m2": round(total_floor_area, 2),
        "energy_performance_index_kwh_m2": epi,
        "assumptions": {
            "ac_cop": ac_cop,
            "cooling_hours_per_year": cooling_hours,
            "lighting_hours_per_year": lighting_hours,
            "equipment_hours_per_year": equipment_hours,
        },
        "confidence": confidence,
        "limitations": limitations,
        "status": ResultStatus.ESTIMATED.value,
    }