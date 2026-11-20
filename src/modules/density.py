"""
Module G — Density and Urban Context.

Computes FAR, ground coverage, open space, and occupancy density.

IMPORTANT: This module calculates urban metrics. It does NOT declare RAJUK
compliance. Compliance is a regulatory determination that requires verified
zone data, plot survey, and authority approval.

Formula summary:
  FAR              = total_floor_area / plot_area
  Ground coverage  = building_footprint / plot_area × 100
  Open space       = (plot_area - footprint) / plot_area × 100
  Occupancy density= occupants / building_footprint

RAJUK DAP reference limits (for display only, not compliance):
  - Max ground coverage by plot size (DAP Table 3)
  - Min open space (DAP Sec 1.8.3-1.8.4): 33-50% depending on occupancy
"""
from __future__ import annotations

from typing import Optional

from src.models.schemas import ConfidenceLevel, ResultStatus


def calculate_far(
    total_floor_area_m2: Optional[float],
    plot_area_m2: Optional[float],
) -> Optional[float]:
    """Calculate FAR = total floor area / plot area.

    Returns None if inputs are missing (insufficient data, not zero).
    """
    if total_floor_area_m2 is None or plot_area_m2 is None or plot_area_m2 <= 0:
        return None
    return round(total_floor_area_m2 / plot_area_m2, 3)


def calculate_ground_coverage(
    footprint_m2: Optional[float],
    plot_area_m2: Optional[float],
) -> Optional[float]:
    """Calculate ground coverage = footprint / plot × 100."""
    if footprint_m2 is None or plot_area_m2 is None or plot_area_m2 <= 0:
        return None
    return round((footprint_m2 / plot_area_m2) * 100, 2)


def calculate_open_space(
    footprint_m2: Optional[float],
    plot_area_m2: Optional[float],
) -> Optional[float]:
    """Calculate open space = (plot - footprint) / plot × 100."""
    if footprint_m2 is None or plot_area_m2 is None or plot_area_m2 <= 0:
        return None
    return round(((plot_area_m2 - footprint_m2) / plot_area_m2) * 100, 2)


def calculate_occupancy_density(
    occupants: int,
    footprint_m2: Optional[float],
) -> Optional[float]:
    """Calculate occupancy density = occupants / footprint."""
    if footprint_m2 is None or footprint_m2 <= 0:
        return None
    return round(occupants / footprint_m2, 3)


def calculate_density(
    total_floor_area_m2: Optional[float],
    plot_area_m2: Optional[float],
    footprint_m2: Optional[float],
    total_occupants: int,
    rajuk_zone: Optional[str] = None,
) -> dict:
    """Calculate all density metrics and return a summary.

    Returns FAR, coverage, open space, occupancy density, and a confidence level.
    Does NOT make compliance claims.
    """
    far = calculate_far(total_floor_area_m2, plot_area_m2)
    coverage = calculate_ground_coverage(footprint_m2, plot_area_m2)
    open_space = calculate_open_space(footprint_m2, plot_area_m2)
    occ_density = calculate_occupancy_density(total_occupants, footprint_m2)

    # Missing data → insufficient
    missing = []
    if far is None:
        missing.append("FAR (need floor area + plot area)")
    if coverage is None:
        missing.append("Ground coverage (need footprint + plot area)")
    if open_space is None:
        missing.append("Open space (need footprint + plot area)")

    if missing:
        confidence = ConfidenceLevel.INSUFFICIENT.value
        status = ResultStatus.INSUFFICIENT_DATA.value
    else:
        confidence = ConfidenceLevel.MEDIUM.value
        status = ResultStatus.ESTIMATED.value

    limitations = [
        "Density metrics are calculated values, NOT regulatory compliance.",
        "RAJUK DAP zone limits require manual lookup; not GIS-verified.",
        "FAR is gross floor area based; net vs gross not distinguished.",
    ]
    if rajuk_zone:
        limitations.append(f"RAJUK zone '{rajuk_zone}' referenced; verify current DAP limits.")

    return {
        "far": far,
        "ground_coverage_percent": coverage,
        "open_space_percent": open_space,
        "occupancy_density_pers_m2": occ_density,
        "total_floor_area_m2": total_floor_area_m2,
        "plot_area_m2": plot_area_m2,
        "footprint_m2": footprint_m2,
        "total_occupants": total_occupants,
        "rajuk_zone": rajuk_zone,
        "missing_data": missing,
        "confidence": confidence,
        "limitations": limitations,
        "status": status,
    }