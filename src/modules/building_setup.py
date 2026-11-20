"""
Module A — Building Setup.

Validates building geometry and produces a normalized context for downstream
calculations. No regulatory compliance is claimed here.
"""
from __future__ import annotations

from typing import Optional

from src.core.exceptions import GeometryError
from src.models.schemas import BuildingCreate, ConfidenceLevel, ResultStatus


def validate_building(building: BuildingCreate) -> dict:
    """Validate building inputs and return a normalized context.

    Raises:
        GeometryError: If footprint exceeds plot, or geometry is impossible.
    """
    errors: list[str] = []
    warnings: list[str] = []

    footprint = building.building_footprint_m2
    plot = building.plot_area_m2

    if footprint is not None and plot is not None:
        if footprint > plot:
            raise GeometryError(
                f"Building footprint ({footprint} m²) exceeds plot area ({plot} m²)."
            )
        coverage = footprint / plot
        if coverage > 0.95:
            warnings.append(
                f"Building footprint covers {coverage * 100:.1f}% of the plot — "
                "check open-space requirements."
            )

    # Total floor area consistency (approximate; rooms are validated separately)
    if building.num_floors and building.building_footprint_m2 and footprint is not None:
        estimated_floor_area = footprint * building.num_floors
        # This is a soft cross-check; we do not fail on it, only note.

    return {
        "validated": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "normalized": {
            "city": building.city,
            "building_type": building.building_type.value,
            "num_floors": building.num_floors,
            "floor_to_floor_height_m": building.floor_to_floor_height_m,
            "plot_area_m2": plot,
            "footprint_m2": footprint,
            "orientation_deg": getattr(building, "orientation_deg", None),
            "structural_system": (
                building.structural_system.value if building.structural_system else None
            ),
        },
    }


def building_summary(building: BuildingCreate) -> dict:
    """Return a human-readable building summary with confidence level."""
    context = validate_building(building)
    if context["errors"]:
        return {
            "status": ResultStatus.INSUFFICIENT_DATA.value,
            "confidence": ConfidenceLevel.INSUFFICIENT.value,
            "context": context,
        }
    return {
        "status": ResultStatus.ESTIMATED.value,
        "confidence": ConfidenceLevel.MEDIUM.value,
        "context": context,
    }