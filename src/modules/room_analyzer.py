"""
Module B — Room and Space Analyzer.

For each room, computes area, volume, area per person, occupancy indicators,
and checks against BNBC occupancy minimums where verified.

All formulas are deterministic and unit-tested (see tests/test_room_analyzer.py).
"""
from __future__ import annotations

from src.models.schemas import RoomCreate, ConfidenceLevel, ResultStatus

# BNBC 2020 Part 3 Ch 2 occupancy minimums (m² per person).
# These are representative screening values; the full code contains
# occupancy-specific tables. Each entry is marked with its source section.
# IMPORTANT: these are screening references, NOT a universal limit.
BNBC_OCCUPANCY_MIN_AREA_M2: dict[str, float] = {
    "Residential": 9.3,   # ~100 ft² per occupant (screening value)
    "Office": 9.3,        # ~100 ft² per occupant
    "Classroom": 1.4,     # ~15 ft² per occupant
    "Hospital": 10.0,     # varies by room; screening value
    "Retail": 3.7,        # ~40 ft² per occupant
    "Storage": 46.5,      # low density
    "Laboratory": 11.2,
    "Assembly": 1.1,      # concentrated assembly
    "Other": 9.3,
}


def analyze_room(room: RoomCreate) -> dict:
    """Compute room metrics and occupancy indicators.

    Returns a dict with all computed values plus a status/confidence.
    """
    area = room.floor_area_m2
    volume = room.volume_m3
    occupants = room.occupants

    # Geometry validation
    geometry_warnings: list[str] = []
    if room.length_m <= 0 or room.width_m <= 0:
        geometry_warnings.append("Room length/width must be positive.")
    if room.height_m <= 0:
        geometry_warnings.append("Room height must be positive.")

    # Area per person
    area_per_person = round(area / occupants, 3) if occupants > 0 else 0.0

    # Occupancy indicator
    bnbc_min = BNBC_OCCUPANCY_MIN_AREA_M2.get(room.room_type.value, 9.3)
    occupancy_passes = area_per_person >= bnbc_min

    # Window ratio (screening only)
    wwr = round((room.window_area_m2 / room.wall_area_m2) * 100, 2) if room.wall_area_m2 > 0 else 0.0

    # Status determination
    if geometry_warnings:
        status = ResultStatus.NEEDS_REVIEW.value
        confidence = ConfidenceLevel.INSUFFICIENT.value
    else:
        status = ResultStatus.ESTIMATED.value
        confidence = ConfidenceLevel.MEDIUM.value

    return {
        "room_id": getattr(room, "id", None),
        "room_name": room.name,
        "room_type": room.room_type.value,
        "floor_area_m2": area,
        "volume_m3": volume,
        "area_per_person_m2": area_per_person,
        "occupants": occupants,
        "bnbc_min_area_per_person_m2": bnbc_min,
        "occupancy_passes_screening": occupancy_passes,
        "window_to_wall_ratio_percent": wwr,
        "geometry_warnings": geometry_warnings,
        "status": status,
        "confidence": confidence,
    }


def analyze_rooms(rooms: list[RoomCreate]) -> dict:
    """Analyze all rooms and return a summary."""
    results = [analyze_room(r) for r in rooms]

    total_area = sum(r["floor_area_m2"] for r in results)
    total_volume = sum(r["volume_m3"] for r in results)
    total_occupants = sum(r["occupants"] for r in results)
    passing = sum(1 for r in results if r["occupancy_passes_screening"])
    below = len(results) - passing

    overall_confidence = (
        ConfidenceLevel.HIGH.value if passing == len(results)
        else ConfidenceLevel.MEDIUM.value if passing > len(results) / 2
        else ConfidenceLevel.LOW.value
    )

    return {
        "rooms": results,
        "summary": {
            "total_rooms": len(results),
            "total_floor_area_m2": round(total_area, 2),
            "total_volume_m3": round(total_volume, 2),
            "total_occupants": total_occupants,
            "rooms_passing_screening": passing,
            "rooms_below_screening": below,
        },
        "overall_confidence": overall_confidence,
        "status": ResultStatus.ESTIMATED.value,
    }