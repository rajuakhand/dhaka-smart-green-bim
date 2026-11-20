"""
Module P2-5 — Sensitivity Analysis.

One-at-a-time (OAT) sensitivity analysis: perturb one input parameter by a
fixed percentage while holding all others at baseline, re-run the metric, and
record the swing.

This identifies which uncertain inputs have the greatest effect on results —
a direct requirement of the project brief (Section 9: Uncertainty & Confidence).

Method:
    For each parameter p with baseline value v:
        low  = run(v * (1 - delta))
        high = run(v * (1 + delta))
        swing = |high_result - low_result|
        elasticity = (pct_change_result) / (pct_change_input)

Elasticity is dimensionless and comparable across parameters with different
units. |elasticity| > 1 means the output is more sensitive than the input.

Limitations (always reported):
    - OAT ignores interactions between parameters.
    - Linear interpolation between low/high; non-linear response is approximated.
    - Only local sensitivity near the baseline, not global.
"""
from __future__ import annotations

from typing import Callable, Optional

from src.core.exceptions import ValidationFailure


def one_at_a_time_sensitivity(
    baseline_inputs: dict,
    metric_function: Callable[[dict], float],
    parameters: Optional[list[str]] = None,
    delta: float = 0.10,
) -> dict:
    """Run OAT sensitivity analysis.

    Args:
        baseline_inputs: baseline parameter dict.
        metric_function: callable(dict) -> float, the metric to test.
        parameters: parameter names to vary (default: all numeric ones).
        delta: fractional perturbation (0.10 = +/-10%).

    Returns:
        Dict with baseline metric, per-parameter swing/elasticity, and a ranking.
    """
    if not callable(metric_function):
        raise ValidationFailure("metric_function must be callable")
    if not (0.0 < delta <= 1.0):
        raise ValidationFailure("delta must be in (0, 1]")

    baseline_value = float(metric_function(dict(baseline_inputs)))
    if baseline_value == 0:
        raise ValidationFailure(
            "Baseline metric is zero; elasticity is undefined. "
            "Choose a non-zero baseline or use absolute swing only."
        )

    if parameters is None:
        parameters = [
            k for k, v in baseline_inputs.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)
        ]

    results: list[dict] = []
    for name in parameters:
        if name not in baseline_inputs:
            continue
        base = baseline_inputs[name]
        if not isinstance(base, (int, float)) or isinstance(base, bool):
            continue
        if base == 0:
            results.append({
                "parameter": name,
                "baseline_value": base,
                "note": "Baseline is zero; elasticity undefined (skipped).",
            })
            continue

        low_inputs = dict(baseline_inputs)
        low_inputs[name] = base * (1.0 - delta)
        high_inputs = dict(baseline_inputs)
        high_inputs[name] = base * (1.0 + delta)

        low_metric = float(metric_function(low_inputs))
        high_metric = float(metric_function(high_inputs))

        swing = abs(high_metric - low_metric)
        pct_metric_change = ((high_metric - low_metric) / baseline_value) * 100.0
        elasticity = pct_metric_change / (delta * 200.0)

        results.append({
            "parameter": name,
            "baseline_value": base,
            "low_value": round(low_inputs[name], 4),
            "high_value": round(high_inputs[name], 4),
            "low_metric": round(low_metric, 4),
            "high_metric": round(high_metric, 4),
            "absolute_swing": round(swing, 4),
            "percent_swing_of_baseline": round(
                (swing / abs(baseline_value)) * 100.0, 2
            ),
            "elasticity": round(elasticity, 3),
            "interpretation": (
                "output more sensitive than input (|e|>1)"
                if abs(elasticity) > 1
                else "output less sensitive than input (|e|<1)"
            ),
        })

    ranked = sorted(
        [r for r in results if "elasticity" in r],
        key=lambda r: abs(r["elasticity"]),
        reverse=True,
    )

    return {
        "method": "One-at-a-time (OAT) perturbation",
        "baseline_metric": round(baseline_value, 4),
        "delta_percent": delta * 100.0,
        "parameters_tested": len([r for r in results if "elasticity" in r]),
        "results": results,
        "ranking_by_influence": [r["parameter"] for r in ranked],
        "most_influential": ranked[0]["parameter"] if ranked else None,
        "least_influential": ranked[-1]["parameter"] if ranked else None,
        "limitations": [
            "OAT ignores interactions between parameters.",
            "Linear interpolation between low/high; non-linear response is approximated.",
            "Only local sensitivity near the baseline, not a global uncertainty analysis.",
            "Elasticity is dimensionless but parameter units differ; compare ranking, not magnitude.",
        ],
        "confidence": "Medium confidence",
    }