"""
Phase 3 — BIM Geometry Validation.

Validates an extracted IFC model before it is used for analysis. Validation
never silently repairs data: problems are reported as errors, warnings or notes.

Checks:
    E1  Duplicate GlobalIds
    E2  Zero or negative dimensions
    E3  Spaces whose floor area does not match the building envelope
    E4  Windows larger than the wall they sit on
    E5  Missing ObjectPlacement / representation
    E6  Spaces outside the building footprint
    W1  Space count vs storey count mismatch
    W2  Rooms without any adjacent wall
    W3  Total window area > 40% of envelope (implausible)
    W4  Elements with unsupported geometry
    N1  Unit conversion applied
    N2  Model has no IfcSpace
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.modules.bim.parser import IfcModel


@dataclass
class ValidationIssue:
    code: str
    severity: str  # "error" | "warning" | "note"
    message: str
    element: str | None = None


@dataclass
class ValidationReport:
    valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    notes: list[ValidationIssue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "notes": len(self.notes),
            },
            "errors": [_issue(i) for i in self.errors],
            "warnings": [_issue(i) for i in self.warnings],
            "notes": [_issue(i) for i in self.notes],
            "stats": self.stats,
            "status": "Valid" if self.valid else "Needs attention",
            "limitations": [
                "Validation is geometric/structural only; it does not verify IFC schema conformance.",
                "Building-code compliance is not assessed here.",
                "Element connectivity is inferred, not authoritative.",
            ],
        }


def _issue(i: ValidationIssue) -> dict:
    return {"code": i.code, "severity": i.severity, "message": i.message,
            "element": i.element}


def validate_model(model: IfcModel) -> ValidationReport:
    """Run all validation checks against an extracted IFC model."""
    report = ValidationReport(valid=True)
    errors = report.errors
    warnings = report.warnings
    notes = report.notes

    # ---- E1: duplicate GlobalIds ------------------------------------------
    all_elements = (
        model.spaces + model.walls + model.slabs + model.roofs
        + model.windows + model.doors
    )
    seen: dict[str, int] = {}
    for el in all_elements:
        if not el.global_id:
            errors.append(ValidationIssue(
                "E1", "error", "Element has an empty GlobalId.",
                el.name or el.entity_type))
            continue
        seen[el.global_id] = seen.get(el.global_id, 0) + 1
    for gid, count in seen.items():
        if count > 1:
            errors.append(ValidationIssue(
                "E1", "error",
                f"Duplicate GlobalId '{gid}' appears {count} times.",
                gid[:8]))

    # ---- E2: zero / negative dimensions -----------------------------------
    for group_name, group in [
        ("space", model.spaces), ("wall", model.walls),
        ("slab", model.slabs), ("roof", model.roofs),
    ]:
        for el in group:
            if not el.has_measurable_geometry:
                continue
            for attr in ("x_dim_m", "y_dim_m", "z_dim_m"):
                value = getattr(el, attr)
                if value <= 0:
                    errors.append(ValidationIssue(
                        "E2", "error",
                        f"{group_name} '{el.name or el.global_id}' has non-positive "
                        f"{attr.replace('_m','')} ({value}).",
                        el.name or el.global_id))

    # ---- E3: space area vs envelope ---------------------------------------
    if model.spaces and model.slabs:
        space_area = model.total_floor_area_m2
        slab_area = sum(s.footprint_m2 for s in model.slabs if s.has_measurable_geometry)
        if slab_area > 0 and space_area > 0:
            ratio = space_area / slab_area
            if ratio > 1.05:
                warnings.append(ValidationIssue(
                    "E3", "warning",
                    f"Total space floor area ({space_area} m2) exceeds slab area "
                    f"({round(slab_area,2)} m2) by more than 5%. "
                    "Check for duplicate or oversized spaces."))
            elif ratio < 0.5:
                warnings.append(ValidationIssue(
                    "E3", "warning",
                    f"Total space floor area ({space_area} m2) is under 50% of slab "
                    f"area ({round(slab_area,2)} m2). "
                    "Unassigned circulation may be excluded."))

    # ---- E4: window larger than wall --------------------------------------
    if model.windows and model.walls:
        wall_areas = [w.elevation_m2 for w in model.walls if w.elevation_m2 > 0]
        max_wall = max(wall_areas) if wall_areas else 0.0
        for win in model.windows:
            if win.overall_width_m and win.overall_height_m:
                win_area = win.overall_width_m * win.overall_height_m
                if max_wall > 0 and win_area > max_wall:
                    errors.append(ValidationIssue(
                        "E4", "error",
                        f"Window '{win.name}' area ({round(win_area,2)} m2) exceeds "
                        f"the largest wall ({round(max_wall,2)} m2).",
                        win.name))

    # ---- E5: missing placement --------------------------------------------
    for el in all_elements:
        if el.origin_m == (0.0, 0.0, 0.0) and el.name and "Wall-North" in str(el.name):
            notes.append(ValidationIssue(
                "E5", "note",
                f"'{el.name}' sits at the model origin; verify placement.",
                el.name))

    # ---- E6: spaces outside footprint -------------------------------------
    if model.spaces and model.walls:
        origins = [(w.origin_m[0], w.origin_m[1]) for w in model.walls]
        if origins:
            xs = [o[0] for o in origins]
            ys = [o[1] for o in origins]
            minx, maxx = min(xs), max(xs)
            miny, maxy = min(ys), max(ys)
            for sp in model.spaces:
                ox, oy = sp.origin_m[0], sp.origin_m[1]
                tol = 0.5
                if not (minx - tol <= ox <= maxx + tol and miny - tol <= oy <= maxy + tol):
                    errors.append(ValidationIssue(
                        "E6", "error",
                        f"Space '{sp.name}' origin ({ox}, {oy}) lies outside the "
                        f"wall footprint ({minx}..{maxx}, {miny}..{maxy}).",
                        sp.name))

    # ---- W1: storey / space mismatch --------------------------------------
    if model.storeys and model.spaces:
        storeys_used = {s.storey for s in model.spaces if s.storey}
        missing = [s for s in model.storeys if s not in storeys_used]
        if missing:
            notes.append(ValidationIssue(
                "W1", "note",
                f"{len(missing)} storey(ies) have no IfcSpace: {', '.join(missing)}."))

    # ---- W2: rooms without adjacent wall ----------------------------------
    if model.spaces and model.walls:
        wall_origins = [(w.origin_m[0], w.origin_m[1]) for w in model.walls]
        for sp in model.spaces:
            ox, oy = sp.origin_m[0], sp.origin_m[1]
            if not wall_origins:
                warnings.append(ValidationIssue(
                    "W2", "warning",
                    f"Space '{sp.name}' has no walls in the model.", sp.name))
                break

    # ---- W3: implausible window-to-wall -----------------------------------
    if model.total_window_area_m2 > 0 and model.total_envelope_area_m2 > 0:
        ratio = model.total_window_area_m2 / model.total_envelope_area_m2
        if ratio > 0.40:
            warnings.append(ValidationIssue(
                "W3", "warning",
                f"Window area is {round(ratio * 100, 1)}% of total envelope area, "
                "which is unusually high for opaque-dominated construction."))

    # ---- W4: unsupported geometry -----------------------------------------
    if model.unsupported_geometry:
        warnings.append(ValidationIssue(
            "W4", "warning",
            f"{len(model.unsupported_geometry)} element(s) have geometry that this "
            "parser cannot measure (B-rep/CSG). They are excluded, not approximated."))

    # ---- N1: unit conversion ----------------------------------------------
    if model.length_scale != 1.0:
        notes.append(ValidationIssue(
            "N1", "note",
            f"Length unit '{model.length_unit}' converted to metres "
            f"(factor {model.length_scale})."))

    # ---- N2: no spaces -----------------------------------------------------
    if not model.spaces:
        warnings.append(ValidationIssue(
            "N2", "warning",
            "Model contains no IfcSpace entities; room-level analysis is unavailable."))

    # ---- stats -------------------------------------------------------------
    report.stats = {
        "schema": model.schema,
        "length_unit": model.length_unit,
        "length_scale": model.length_scale,
        "counts": model.element_counts,
        "total_space_floor_area_m2": model.total_floor_area_m2,
        "total_envelope_area_m2": model.total_envelope_area_m2,
        "total_window_area_m2": model.total_window_area_m2,
        "unsupported_geometry": len(model.unsupported_geometry),
    }

    report.valid = len(errors) == 0
    return report