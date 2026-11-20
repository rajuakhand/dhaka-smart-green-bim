"""
Module D — Preliminary Daylight Screening.

Screens whether a room is likely to achieve adequate daylight based on
glazing ratio (window area / floor area) and simple shading assessment.

IMPORTANT: This is NOT a daylight simulation. No lux levels, DF, sDA, or ASE
are claimed. Screening uses BNBC 2020 Sec 2.14.6.1: glazed area >= 10% of
floor area.
"""
from __future__ import annotations

from src.models.schemas import RoomCreate, ConfidenceLevel, ResultStatus

# BNBC 2020 Sec 2.14.6.1: exterior glazing >= 10% of floor area
BNBC_MIN_GLAZING_RATIO = 0.10

# Approximate visible transmittance (VT) by glazing type
GLAZING_VT = {
    "Clear": 0.90,
    "Tinted": 0.60,
    "Double low-E": 0.75,
    "Other": 0.50,
}


def screen_room_daylight(room: RoomCreate) -> dict:
    """Screen a single room for daylight potential.

    Returns a dict with WWR, BNBC 10% check, effective glazing with obstruction,
    and preliminary daylight potential label.
    """
    floor_area = room.floor_area_m2
    window_area = room.window_area_m2
    wall_area = room.wall_area_m2

    # Window-to-wall ratio
    wwr = round((window_area / wall_area) * 100, 2) if wall_area > 0 else 0.0

    # BNBC 10% glazing check
    glazing_ratio = round((window_area / floor_area) * 100, 2) if floor_area > 0 else 0.0
    passes_bnbc = (window_area / floor_area) >= BNBC_MIN_GLAZING_RATIO if floor_area > 0 else False

    # Obstruction reduction factor (simple linear model)
    # If obstruction height > 0, reduce effective glazing by a simple factor.
    # This is a screening simplification, not a geometric shadow calculation.
    obstruction = room.external_obstruction_height_m
    obstruction_factor = 0.0
    if obstruction > 0:
        # Simplified: each 1m of obstruction above eye level (say 2m) reduces
        # effective glazing by ~5%. Cap at 50% reduction.
        obstruction_factor = min(0.5, (obstruction / 2.0) * 0.05)
    effective_glazing = round(glazing_ratio * (1 - obstruction_factor), 2)

    # Glazing visible transmittance
    vt = GLAZING_VT.get(room.glazing_type.value if room.glazing_type else "Clear", 0.9)

    # Overhang shading
    has_overhang = room.shading_type in ("Overhang", "Both") if room.shading_type else False

    # Daylight potential label (preliminary, not verified)
    if effective_glazing >= 10:
        potential = "Adequate"
    elif effective_glazing >= 5:
        potential = "Marginal"
    else:
        potential = "Insufficient"

    # Confidence
    if passes_bnbc and obstruction_factor == 0:
        confidence = ConfidenceLevel.MEDIUM.value
        status = ResultStatus.ESTIMATED.value
    else:
        confidence = ConfidenceLevel.LOW.value
        status = ResultStatus.INSUFFICIENT_DATA.value

    limitations = [
        "Screening only; no lux, DF, sDA, or ASE simulation.",
        "Obstruction reduction is a simple linear model, not geometric shadow analysis.",
    ]

    recommendations: list[str] = []
    if not passes_bnbc:
        recommendations.append(
            f"Increase glazing to at least 10% of floor area "
            f"(current: {glazing_ratio:.1f}%, required: 10%)."
        )
    if obstruction > 0 and effective_glazing < 10:
        recommendations.append(
            f"External obstruction ({obstruction} m) reduces effective daylight; "
            "consider light shelves or lighter finishes."
        )
    if not has_overhang and wwr > 30:
        recommendations.append(
            "Consider adding overhangs to reduce solar heat gain while maintaining daylight."
        )

    return {
        "room_id": getattr(room, "id", None),
        "room_name": room.name,
        "window_area_m2": window_area,
        "wall_area_m2": wall_area,
        "wwr_percent": wwr,
        "bnbc_min_10_percent": passes_bnbc,
        "effective_glazing_with_obstruction_percent": effective_glazing,
        "glazing_vt": vt,
        "overhang_shading": has_overhang,
        "daylight_potential": potential,
        "confidence": confidence,
        "limitations": limitations,
        "recommendations": recommendations,
        "status": status,
    }


def screen_all_rooms_daylight(rooms: list[RoomCreate]) -> dict:
    """Screen all rooms for daylight and return a summary."""
    results = [screen_room_daylight(r) for r in rooms]

    passing = sum(1 for r in results if r["bnbc_min_10_percent"])
    below = len(results) - passing

    if passing == len(results):
        confidence = ConfidenceLevel.HIGH.value
    elif passing > len(results) / 2:
        confidence = ConfidenceLevel.MEDIUM.value
    else:
        confidence = ConfidenceLevel.LOW.value

    return {
        "rooms": results,
        "summary": {
            "rooms_screened": len(results),
            "rooms_above_minimum": passing,
            "rooms_below_minimum": below,
        },
        "confidence": confidence,
        "status": ResultStatus.ESTIMATED.value,
        "limitations": [
            "Screening only; no daylight simulation (sDA/ASE).",
            "WWR screening does not account for room orientation or external geometry.",
        ],
    }