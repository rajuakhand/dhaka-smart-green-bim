"""
Module I — Design Optimization Comparison.

Compares a baseline design against one or more alternatives using the same
calculation engine. All comparisons use the same baseline assumptions.

IMPORTANT: This module does NOT promise savings. It only reports the difference
between two explicitly-defined cases. Savings claims require valid comparison.
"""
from __future__ import annotations

from src.models.schemas import ConfidenceLevel
from src.modules.energy import estimate_building_energy
from src.modules.ventilation import screen_all_rooms
from src.modules.daylight import screen_all_rooms_daylight


def compare_case(
    baseline_result: float,
    alternative_result: float,
    metric_name: str,
) -> dict:
    """Compute difference and percentage difference between two values."""
    diff = alternative_result - baseline_result
    pct = round((diff / baseline_result) * 100, 2) if baseline_result != 0 else 0.0
    return {
        "metric_name": metric_name,
        "baseline_value": baseline_result,
        "alternative_value": alternative_result,
        "difference": round(diff, 2),
        "percent_difference": pct,
    }


def compare_energy_cases(
    rooms: list,
    baseline_assumptions: dict,
    alternatives: list[dict],
) -> dict:
    """Compare baseline energy against alternatives with changed assumptions.

    Args:
        rooms: list of RoomCreate objects.
        baseline_assumptions: dict with ac_cop, cooling_hours, etc.
        alternatives: list of dicts, each with 'name' and changed assumptions.
    """
    # Baseline
    baseline = estimate_building_energy(rooms, **baseline_assumptions)
    baseline_epi = baseline["energy_performance_index_kwh_m2"]

    results: list[dict] = []
    for alt in alternatives:
        # Merge baseline with overrides
        merged = {**baseline_assumptions, **alt.get("changes", {})}
        alt_energy = estimate_building_energy(rooms, **merged)
        alt_epi = alt_energy["energy_performance_index_kwh_m2"]

        comparison = compare_case(baseline_epi, alt_epi, "EPI (kWh/m²/yr)")
        results.append({
            "name": alt["name"],
            "changes": alt.get("changes", {}),
            "baseline_epi": baseline_epi,
            "alternative_epi": alt_epi,
            "difference": comparison["difference"],
            "percent_difference": comparison["percent_difference"],
            "confidence": ConfidenceLevel.MEDIUM.value,
        })

    return {
        "baseline_module": "E",
        "baseline_metric_name": "EPI (kWh/m²/yr)",
        "baseline_metric_value": baseline_epi,
        "alternatives": results,
        "method": "Preliminary energy estimator (same assumptions, changed inputs)",
        "limitations": [
            "Comparison uses preliminary estimates, not simulation.",
            "Percentages are relative to baseline; absolute values may vary with weather.",
        ],
    }


def compare_ventilation_cases(
    rooms: list,
) -> dict:
    """Compare baseline vs alternative ventilation scenarios."""
    baseline = screen_all_rooms(rooms)
    baseline_passing = baseline["summary"]["rooms_passing"]

    return {
        "baseline_module": "C",
        "baseline_metric_name": "Rooms passing ventilation screening",
        "baseline_metric_value": baseline_passing,
        "alternatives": [],
        "method": "Preliminary ventilation screening",
        "limitations": ["Screening only; no ACH calculation."],
    }