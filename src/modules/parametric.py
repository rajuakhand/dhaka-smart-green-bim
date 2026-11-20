"""
Module P2-6 — Parametric Design Optimization.

Grid search over discrete design variables to find the combination that
minimises (or maximises) a chosen metric, subject to the same baseline
assumptions.

Search strategy:
    - Exhaustive grid search over user-supplied candidate values.
    - For larger spaces, a seeded random search is available.
    - Constraint filtering (e.g., reject designs failing a minimum DF).

All evaluations use the same deterministic calculation engine as the rest of
the platform — no simulation engine is required or implied.

Method:
    For each candidate combination c in the design space:
        metric = f(c)
        if constraints(c) fail: skip
        track best
    Return the ranking plus the Pareto-style trade-off table when a second
    metric is supplied.

Limitations (always reported):
    - Only the supplied candidate values are searched; no continuous gradients.
    - Constraints are screening rules, not code compliance.
    - Each candidate is a preliminary estimate, not a simulation.
"""
from __future__ import annotations

import itertools
import random
from typing import Callable, Optional

from src.core.exceptions import ValidationFailure


def grid_search(
    design_space: dict[str, list],
    objective_function: Callable[[dict], float],
    constraints: Optional[dict[str, Callable[[dict], bool]]] = None,
    secondary_metric: Optional[Callable[[dict], float]] = None,
    maximise: bool = False,
) -> dict:
    """Exhaustive grid search over a design space.

    Args:
        design_space: {parameter_name: [candidate values]}
        objective_function: callable(design_dict) -> float (lower is better
            unless maximise=True).
        constraints: {name: callable(design_dict) -> bool}; False rejects.
        secondary_metric: optional second metric for trade-off reporting.
        maximise: if True, the largest objective value wins.

    Returns:
        Dict with best design, ranking, evaluated count, and limitations.
    """
    if not design_space:
        raise ValidationFailure("design_space must not be empty")
    if not callable(objective_function):
        raise ValidationFailure("objective_function must be callable")
    if any(not isinstance(v, (list, tuple)) or not v for v in design_space.values()):
        raise ValidationFailure("each design_space value must be a non-empty list")

    names = list(design_space.keys())
    candidates = list(itertools.product(*(design_space[n] for n in names)))
    total = len(candidates)

    evaluated: list[dict] = []
    rejected = 0
    for combo in candidates:
        design = dict(zip(names, combo))
        if constraints:
            if not all(fn(design) for fn in constraints.values()):
                rejected += 1
                continue
        value = float(objective_function(design))
        row = {
            "design": design,
            "objective": round(value, 4),
        }
        if secondary_metric is not None:
            row["secondary"] = round(float(secondary_metric(design)), 4)
        evaluated.append(row)

    if not evaluated:
        return {
            "method": "Exhaustive grid search",
            "evaluated": 0,
            "rejected": rejected,
            "best": None,
            "ranking": [],
            "limitations": ["All candidates were rejected by constraints."],
            "status": "Insufficient data",
        }

    evaluated.sort(key=lambda r: r["objective"], reverse=maximise)
    best = evaluated[0]

    return {
        "method": "Exhaustive grid search",
        "objective_direction": "maximise" if maximise else "minimise",
        "design_space_size": total,
        "evaluated": len(evaluated),
        "rejected_by_constraints": rejected,
        "best": best,
        "baseline_reference": None,
        "ranking": evaluated,
        "limitations": [
            "Only the supplied candidate values are searched; no continuous gradients.",
            "Constraints are screening rules, not regulatory compliance.",
            "Each candidate is a preliminary estimate, not a simulation.",
            "Parameter interactions are evaluated jointly only within the grid supplied.",
        ],
        "status": "Estimated",
        "confidence": "Medium confidence",
    }


def random_search(
    design_space: dict[str, list],
    objective_function: Callable[[dict], float],
    n_samples: int = 200,
    constraints: Optional[dict[str, Callable[[dict], bool]]] = None,
    maximise: bool = False,
    seed: int = 42,
) -> dict:
    """Seeded random search for large design spaces.

    Deterministic for a given seed — the same seed always returns the same
    result, which is required for reproducible testing.
    """
    if n_samples <= 0:
        raise ValidationFailure("n_samples must be positive")
    if not design_space:
        raise ValidationFailure("design_space must not be empty")
    if not callable(objective_function):
        raise ValidationFailure("objective_function must be callable")

    rng = random.Random(seed)
    names = list(design_space.keys())
    evaluated: list[dict] = []
    rejected = 0

    for _ in range(n_samples):
        design = {n: rng.choice(design_space[n]) for n in names}
        if constraints and not all(fn(design) for fn in constraints.values()):
            rejected += 1
            continue
        value = float(objective_function(design))
        evaluated.append({"design": design, "objective": round(value, 4)})

    if not evaluated:
        return {
            "method": "Seeded random search",
            "evaluated": 0,
            "rejected": rejected,
            "best": None,
            "ranking": [],
            "seed": seed,
            "limitations": ["All candidates were rejected by constraints."],
            "status": "Insufficient data",
        }

    evaluated.sort(key=lambda r: r["objective"], reverse=maximise)
    return {
        "method": "Seeded random search",
        "objective_direction": "maximise" if maximise else "minimise",
        "n_samples_requested": n_samples,
        "evaluated": len(evaluated),
        "rejected_by_constraints": rejected,
        "best": evaluated[0],
        "ranking": evaluated,
        "seed": seed,
        "reproducible": True,
        "limitations": [
            "Stochastic sample of the design space; the true optimum may be missed.",
            "Results are reproducible for a fixed seed but not guaranteed optimal.",
            "Each candidate is a preliminary estimate, not a simulation.",
        ],
        "status": "Estimated",
        "confidence": "Low confidence",
    }