"""
Module C — Preliminary Natural Ventilation Screening.

This module screens whether a room is likely to achieve natural ventilation
based on opening ratios and geometry. It does NOT calculate air-change rate.

IMPORTANT: Window area ratio is NOT equivalent to airflow. This module only
provides a screening indicator. No verified ACH is claimed.
"""
from __future__ import annotations

from src.models.schemas import RoomCreate, ConfidenceLevel, ResultStatus

# BNBC 2020 Sec 2.14.6.1: openable area >= 5% of floor area
BNBC_MIN_OPENING_RATIO = 0.05


def screen_room_ventilation(room: RoomCreate) -> dict:
    """Screen a single room for natural ventilation potential.

    Returns a dict with opening ratio, pass/fail vs BNBC 5%, and
    preliminary cross-ventilation feasibility based on geometry.
    """
    floor_area = room.floor_area_m2
    openable_area = room.openable_window_area_m2

    # Opening ratio
    if floor_area > 0:
        opening_ratio = round((openable_area / floor_area) * 100, 2)
    else:
        opening_ratio = 0.0

    # BNBC 5% check
    passes_bnbc = (openable_area / floor_area) >= BNBC_MIN_OPENING_RATIO if floor_area > 0 else False

    # Room geometry for cross-ventilation screening
    # Rule of thumb: cross-ventilation possible if room has openings on
    # opposite walls and depth <= 2.5 × ceiling height.
    room_depth = max(room.length_m, room.width_m)  # simplified depth
    depth_to_height_ratio = round(room_depth / room.height_m, 2) if room.height_m > 0 else 0.0

    # Cross-ventilation potential: need openings on 2+ walls.
    # For screening, we assume the room has windows on all 4 walls if
    # window_area > 0. This is a simplification; detailed analysis requires
    # wall-by-wall window data (Phase 2).
    window_on_multiple_walls = room.window_area_m2 > 0
    depth_favorable = depth_to_height_ratio <= 2.5
    cross_vent_possible = window_on_multiple_walls and depth_favorable
    single_sided_only = not cross_vent_possible

    # Obstruction flag
    obstruction_flag = room.external_obstruction_height_m > 0

    # Confidence
    if passes_bnbc:
        confidence = ConfidenceLevel.MEDIUM.value
        status = ResultStatus.ESTIMATED.value
    else:
        confidence = ConfidenceLevel.LOW.value
        status = ResultStatus.INSUFFICIENT_DATA.value

    # Limitations
    limitations = [
        "Screening only; not ACH calculation.",
        "Cross-ventilation feasibility requires wall-by-wall opening data (Phase 2).",
    ]
    if obstruction_flag:
        limitations.append(
            f"External obstruction height {room.external_obstruction_height_m} m may reduce "
            "wind access; not modelled in this screening."
        )

    # Recommendations
    recommendations: list[str] = []
    if not passes_bnbc:
        recommendations.append(
            f"Increase openable window area to at least 5% of floor area "
            f"(current: {opening_ratio:.1f}%, required: 5%)."
        )
    if single_sided_only:
        recommendations.append(
            "Consider cross-ventilation: add openings on opposite walls."
        )
    if depth_favorable is False:
        recommendations.append(
            f"Room depth ({room_depth:.1f} m) may limit natural ventilation; "
            "consider mechanical ventilation."
        )

    return {
        "room_id": getattr(room, "id", None),
        "room_name": room.name,
        "floor_area_m2": floor_area,
        "openable_window_area_m2": openable_area,
        "opening_ratio_percent": opening_ratio,
        "bnbc_min_5_percent": passes_bnbc,
        "passes_screening": passes_bnbc,
        "room_depth_m": room_depth,
        "depth_to_height_ratio": depth_to_height_ratio,
        "cross_ventilation_possible": cross_vent_possible,
        "single_sided_only": single_sided_only,
        "obstruction_flag": obstruction_flag,
        "confidence": confidence,
        "limitations": limitations,
        "recommendations": recommendations,
        "status": status,
    }


def screen_all_rooms(rooms: list[RoomCreate]) -> dict:
    """Screen all rooms for ventilation and return a summary."""
    results = [screen_room_ventilation(r) for r in rooms]

    passing = sum(1 for r in results if r["passes_screening"])
    below = len(results) - passing
    needs_review = [r["room_name"] for r in results if r["status"] == ResultStatus.INSUFFICIENT_DATA.value]

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
            "rooms_passing": passing,
            "rooms_below_minimum": below,
            "needs_review": needs_review,
        },
        "confidence": confidence,
        "status": ResultStatus.ESTIMATED.value,
        "limitations": [
            "Screening only; no ACH or airflow calculation.",
            "Cross-ventilation is a binary indicator, not a flow rate.",
        ],
    }