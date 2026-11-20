"""
Module F — Operational Carbon Calculator.

Computes operational electricity emissions:
    Operational electricity emissions = electricity consumption × emission factor

Uses a verified emission factor with explicit source, year, and boundary.

IMPORTANT: This module does NOT compute embodied carbon (no verified Bangladesh
EPDs exist). Embodied carbon is explicitly null until a verified source is
available.

Emission factor sources (in priority order):
1. DoE Grid Emission Factor (GEF) — official Bangladesh government
2. Ember/OWID — international, CC BY 4.0
3. User-supplied — labelled as user input
"""
from __future__ import annotations

from src.core.config import DATA_DIR
from src.core.exceptions import SourceUnavailableError
from src.models.schemas import ConfidenceLevel, ResultStatus

# Verified emission factors (kg CO2e per kWh)
# These are loaded from the source registry; do not hardcode in production.
EMISSION_FACTORS: dict[str, dict] = {
    "DoE-GEF": {
        "year": 2022,
        "factor_kg_co2_per_kwh": 0.62,
        "scope": "location-based (Scope 2)",
        "verified": True,
        "source": "DoE Grid Emission Factor 2019-22 (23 Jan 2025)",
    },
    "Ember-OWID": {
        "year": 2025,
        "factor_kg_co2_per_kwh": 0.696,
        "scope": "generation-based",
        "verified": True,
        "source": "Ember/OWID (CC BY 4.0)",
    },
    "User-supplied": {
        "year": 2026,
        "factor_kg_co2_per_kwh": 0.696,  # placeholder; user must override
        "scope": "user-defined",
        "verified": False,
        "source": "User-supplied",
    },
}


def calculate_carbon(
    electricity_kwh_per_year: float,
    emission_factor_source: str = "DoE-GEF",
) -> dict:
    """Calculate operational electricity emissions.

    Args:
        electricity_kwh_per_year: Annual electricity consumption (kWh).
        emission_factor_source: Source key (DoE-GEF, Ember-OWID, User-supplied).

    Returns:
        Dict with emission result, source metadata, and confidence.
    """
    if electricity_kwh_per_year < 0:
        raise ValueError("Electricity consumption must be non-negative.")

    ef_data = EMISSION_FACTORS.get(emission_factor_source)
    if ef_data is None:
        raise SourceUnavailableError(f"Emission factor source '{emission_factor_source}' not found.")

    factor = ef_data["factor_kg_co2_per_kwh"]

    # Operational emissions: kWh × kg CO2e/kWh = kg CO2e
    emissions_kg = electricity_kwh_per_year * factor
    emissions_t = emissions_kg / 1000.0

    # Confidence
    confidence = ConfidenceLevel.HIGH.value if ef_data["verified"] else ConfidenceLevel.LOW.value

    limitations = [
        "Only operational electricity emissions; no embodied, transport, or end-of-life.",
        "Grid emission factor is annual average; marginal emissions not considered.",
    ]
    if not ef_data["verified"]:
        limitations.append("Emission factor is user-supplied and unverified.")

    return {
        "electricity_kwh_per_year": round(electricity_kwh_per_year, 2),
        "emission_factor_kg_co2_per_kwh": factor,
        "emission_factor_source": emission_factor_source,
        "emission_factor_year": ef_data["year"],
        "emission_scope": ef_data["scope"],
        "operational_emissions_kg_co2e_per_year": round(emissions_kg, 2),
        "operational_emissions_t_co2e_per_year": round(emissions_t, 3),
        "embodied_carbon": None,
        "confidence": confidence,
        "limitations": limitations,
        "status": ResultStatus.ESTIMATED.value,
    }