"""
Module H — Structural Risk Screening.

This module is NOT a structural assessment. It collects relevant information
and produces review flags and missing-information lists.

IMPORTANT: All structural safety conclusions require a qualified structural
engineer. This module never claims structural safety.

Screening triggers:
- Building height > 6 floors → BNBC Part 6 seismic review
- Building age > 20 years → material degradation review
- Structural system unknown → missing info
- Foundation/soil info missing → missing info
"""
from __future__ import annotations

from src.models.schemas import ConfidenceLevel, ResultStatus


def screen_structural(
    num_floors: int,
    construction_year: int | None,
    structural_system: str | None,
    soil_info_available: bool = False,
    foundation_info_available: bool = False,
    seismic_zone_verified: bool = False,
) -> dict:
    """Screen a building for structural review flags.

    Returns missing info list and review flags. Does NOT assess safety.
    """
    flags: list[dict] = []
    missing_info: list[str] = []

    # Height review
    if num_floors > 6:
        flags.append({
            "flag_id": "HEIGHT_SEISMIC",
            "description": f"Building has {num_floors} floors (>6): seismic design per BNBC Part 6 required.",
            "severity": "High",
        })

    # Age review
    if construction_year is not None:
        age = 2026 - construction_year
        if age > 20:
            flags.append({
                "flag_id": "AGE_DEGRADATION",
                "description": f"Building age is {age} years (>20): material degradation review needed.",
                "severity": "Medium",
            })
    else:
        missing_info.append("Construction year not provided.")

    # Structural system
    if structural_system is None or structural_system == "Unknown":
        missing_info.append("Structural system not specified.")

    # Soil / foundation
    if not soil_info_available:
        missing_info.append("Soil investigation / geotechnical report not available.")
    if not foundation_info_available:
        missing_info.append("Foundation type and details not provided.")

    # Seismic zone
    if not seismic_zone_verified:
        missing_info.append("Seismic zone verification per BNBC not confirmed.")

    # Review required?
    review_required = bool(flags) or bool(missing_info)

    return {
        "missing_information": missing_info,
        "flags": flags,
        "review_required": review_required,
        "disclaimer": (
            "This is NOT a structural assessment. Requires a qualified structural engineer "
            "for any safety determination."
        ),
        "confidence": ConfidenceLevel.INSUFFICIENT.value,
        "status": ResultStatus.NEEDS_REVIEW.value if review_required else ResultStatus.INSUFFICIENT_DATA.value,
    }