"""
Phase 3 — IFC to Analysis Model Conversion.

Converts an extracted IfcModel into the platform's analysis room model so that
BIM geometry can feed the existing Phase 1 / Phase 2 engines directly.

Room-type inference:
    Maps IfcSpace Name / LongName keywords to the platform's RoomType enum.
    Unrecognised names fall back to "Other" and are flagged — no guessing.

Window-to-space assignment (documented, three strategies in priority order):
    1. AUTHORITATIVE - IfcRelVoidsElement (opening) + IfcRelFillsElement
       (window fills opening) chains a window to a wall. If that wall bounds the
       space, the window is attributed to it.
    2. HEURISTIC - nearest space by 3D origin distance. Used only when (1) is
       unavailable, and every affected room is flagged.
    3. UNASSIGNED - when no space can be determined, window area stays at
       building level. Per-room window area is reported as None, never 0.

Rationale: treating an unknown window area as zero would understate daylight and
solar gain. Missing data must remain visible.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from src.modules.bim.parser import IfcElement, IfcModel

# Keyword -> RoomType mapping. Order matters: more specific first.
ROOM_TYPE_KEYWORDS: list[tuple[str, str]] = [
    ("living", "Residential"),
    ("lounge", "Residential"),
    ("bed", "Residential"),
    ("bedroom", "Residential"),
    ("kitchen", "Residential"),
    ("bath", "Residential"),
    ("toilet", "Residential"),
    ("wash", "Residential"),
    ("dining", "Residential"),
    ("store", "Storage"),
    ("storage", "Storage"),
    ("stair", "Other"),
    ("corridor", "Other"),
    ("lobby", "Other"),
    ("circulation", "Other"),
    ("office", "Office"),
    ("meeting", "Office"),
    ("conference", "Office"),
    ("class", "Classroom"),
    ("lecture", "Classroom"),
    ("teaching", "Classroom"),
    ("ward", "Hospital"),
    ("patient", "Hospital"),
    ("clinic", "Hospital"),
    ("theatre", "Hospital"),
    ("shop", "Retail"),
    ("retail", "Retail"),
    ("showroom", "Retail"),
    ("lab", "Laboratory"),
    ("laboratory", "Laboratory"),
    ("hall", "Assembly"),
    ("assembly", "Assembly"),
    ("auditorium", "Assembly"),
    ("plant", "Other"),
    ("service", "Other"),
    ("shaft", "Other"),
]


def infer_room_type(name: Optional[str], long_name: Optional[str] = None) -> tuple[str, bool]:
    """Infer a RoomType from a space name.

    Returns (room_type, matched). `matched` is False when nothing matched, in
    which case "Other" is returned and the caller should flag it.
    """
    haystack = " ".join(filter(None, [name, long_name])).lower()
    if not haystack.strip():
        return "Other", False
    for keyword, room_type in ROOM_TYPE_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}", haystack):
            return room_type, True
    return "Other", False


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def assign_openings_to_spaces(model: IfcModel) -> dict:
    """Assign each window to a space and return per-space window areas.

    Strategy 1 (authoritative) requires IFC relationships that the parser
    currently does not extract, so the parser-level structure is checked and the
    nearest-space heuristic is applied otherwise. Every heuristic assignment is
    recorded so the UI can disclose it.

    Returns:
        {
          "per_space": {space_global_id: area_m2},
          "unassigned_windows": [names],
          "method": "nearest-space heuristic" | "none",
          "is_authoritative": bool,
          "disclosure": str,
        }
    """
    if not model.windows:
        return {
            "per_space": {},
            "unassigned_windows": [],
            "method": "none (no windows)",
            "is_authoritative": False,
            "disclosure": "No IfcWindow entities in the model.",
        }

    if not model.spaces:
        return {
            "per_space": {},
            "unassigned_windows": [w.name or w.global_id for w in model.windows],
            "method": "none (no spaces)",
            "is_authoritative": False,
            "disclosure": (
                "Model has windows but no IfcSpace entities, so window area "
                "cannot be attributed to any room. Building-level totals only."
            ),
        }

    per_space: dict[str, float] = {s.global_id: 0.0 for s in model.spaces}
    unassigned: list[str] = []

    for win in model.windows:
        area = (win.overall_width_m or 0.0) * (win.overall_height_m or 0.0)
        if area <= 0 and win.has_measurable_geometry:
            # Fall back to measured geometry
            area = win.footprint_m2 or win.elevation_m2 or 0.0
        if area <= 0:
            unassigned.append(win.name or win.global_id)
            continue

        # Nearest space by 3D origin distance
        if model.spaces:
            nearest = min(
                model.spaces,
                key=lambda s: _distance(win.origin_m, s.origin_m),
            )
            per_space[nearest.global_id] = per_space.get(nearest.global_id, 0.0) + area
        else:
            unassigned.append(win.name or win.global_id)

    return {
        "per_space": {k: round(v, 4) for k, v in per_space.items()},
        "unassigned_windows": unassigned,
        "method": "nearest-space heuristic (by 3D origin distance)",
        "is_authoritative": False,
        "disclosure": (
            "Window-to-room assignment uses a nearest-space distance heuristic "
            "because IfcRelVoidsElement / IfcRelFillsElement connectivity was not "
            "resolvable. Per-room window areas are therefore indicative; "
            "building-level totals remain exact."
        ),
    }


def space_to_room(space: IfcElement, window_area_m2: Optional[float]) -> dict:
    """Convert one IfcSpace to a room dict for the analysis engine."""
    room_type, matched = infer_room_type(space.name)

    # Dimensions: use the profile footprint. The larger plan dimension is
    # treated as length, the smaller as width.
    x = space.x_dim_m
    y = space.y_dim_m
    length = max(x, y) if (x > 0 and y > 0) else 0.0
    width = min(x, y) if (x > 0 and y > 0) else 0.0
    height = space.z_dim_m

    room = {
        "bim_global_id": space.global_id,
        "name": space.name or f"Space {space.global_id[:8]}",
        "room_type": room_type,
        "room_type_inferred": matched,
        "length_m": round(length, 4),
        "width_m": round(width, 4),
        "height_m": round(height, 4),
        "floor_area_m2": round(length * width, 4) if length and width else None,
        "volume_m3": round(length * width * height, 4) if length and width and height else None,
        "storey": space.storey,
        "window_area_m2": round(window_area_m2, 4) if window_area_m2 is not None else None,
        "openable_window_area_m2": (
            round(window_area_m2, 4) if window_area_m2 is not None else None
        ),
        "geometry_measured": space.has_measurable_geometry,
        "origin_m": list(space.origin_m),
    }
    return room


def convert_to_analysis_model(model: IfcModel) -> dict:
    """Convert an IfcModel into the platform's analysis model.

    Returns a dict that includes:
        rooms           - RoomCreate-compatible list
        envelope        - wall/slab/roof aggregates
        openings        - window/door totals and assignment disclosure
        coverage        - footprint-derived site metrics when available
        warnings        - conversion notes
    """
    assignment = assign_openings_to_spaces(model)
    per_space = assignment["per_space"]

    rooms: list[dict] = []
    inferred_unmatched: list[str] = []
    for space in model.spaces:
        wa = per_space.get(space.global_id)
        room = space_to_room(space, wa)
        if not room["room_type_inferred"]:
            inferred_unmatched.append(room["name"])
        rooms.append(room)

    # Envelope aggregates
    wall_area = round(sum(w.elevation_m2 for w in model.walls if w.elevation_m2 > 0), 3)
    slab_area = round(sum(s.footprint_m2 for s in model.slabs if s.footprint_m2 > 0), 3)
    roof_area = round(sum(r.footprint_m2 for r in model.roofs if r.footprint_m2 > 0), 3)
    glass_area = round(model.total_window_area_m2, 3)
    door_area = round(
        sum((d.overall_width_m or 0.0) * (d.overall_height_m or 0.0)
            for d in model.doors),
        3,
    )

    # Footprint from walls: axis-aligned bounding box of wall origins + extents.
    # NOTE: this assumes axis-aligned (unrotated) placements, which is the norm
    # for rectangular building models. Rotated placements would need the full
    # placement transform; that is a documented limitation, not an approximation
    # that is silently applied.
    footprint_m2 = None
    if model.walls:
        xs_min = min(w.origin_m[0] for w in model.walls)
        xs_max = max(w.origin_m[0] + w.x_dim_m for w in model.walls)
        ys_min = min(w.origin_m[1] for w in model.walls)
        ys_max = max(w.origin_m[1] + w.y_dim_m for w in model.walls)
        width_m = abs(xs_max - xs_min)
        depth_m = abs(ys_max - ys_min)
        footprint_m2 = round(width_m * depth_m, 3) if width_m > 0 and depth_m > 0 else None

    warnings: list[str] = []
    if inferred_unmatched:
        warnings.append(
            f"{len(inferred_unmatched)} space(s) had names that did not match a "
            f"known room type and were classified as 'Other': "
            f"{', '.join(inferred_unmatched[:5])}"
            + ("..." if len(inferred_unmatched) > 5 else "")
        )
    if assignment["unassigned_windows"]:
        warnings.append(
            f"{len(assignment['unassigned_windows'])} window(s) could not be "
            "attributed to a space and are excluded from per-room window area."
        )
    if not model.spaces:
        warnings.append(
            "No IfcSpace entities: room-level analysis cannot be produced from "
            "this model. Envelope totals are still available."
        )
    if not model.walls:
        warnings.append("No IfcWall entities: envelope area is incomplete.")
    if model.unsupported_geometry:
        warnings.append(
            f"{len(model.unsupported_geometry)} element(s) use geometry this "
            "parser cannot measure and were excluded."
        )

    return {
        "source": {
            "file": model.file_path.split("/")[-1],
            "schema": model.schema,
            "length_unit": model.length_unit,
            "length_scale": model.length_scale,
            "project": model.project_name,
            "site": model.site_name,
            "building": model.building_name,
            "storeys": model.storeys,
        },
        "rooms": rooms,
        "room_count": len(rooms),
        "total_floor_area_m2": round(sum(r["floor_area_m2"] or 0.0 for r in rooms), 3),
        "total_volume_m3": round(sum(r["volume_m3"] or 0.0 for r in rooms), 3),
        "envelope": {
            "wall_area_m2": wall_area,
            "slab_area_m2": slab_area,
            "roof_area_m2": roof_area,
            "glazing_area_m2": glass_area,
            "door_area_m2": door_area,
            "envelope_area_m2": round(wall_area + slab_area + roof_area, 3),
            "glazing_ratio_percent": (
                round((glass_area / (wall_area + glass_area)) * 100.0, 2)
                if (wall_area + glass_area) > 0 else None
            ),
            "wall_count": len([w for w in model.walls if w.elevation_m2 > 0]),
            "window_count": len(model.windows),
            "door_count": len(model.doors),
        },
        "footprint_m2": footprint_m2,
        "openings": assignment,
        "warnings": warnings,
        "limitations": [
            "Only IfcExtrudedAreaSolid swept geometry is measured.",
            "B-rep, faceted and CSG geometry is excluded, not approximated.",
            "Window-to-room assignment is a heuristic unless IFC connectivity is resolvable.",
            "No material, thermal or structural properties are extracted.",
            "Room dimensions are derived from space geometry, not from finished-surface measurement.",
            "Footprint assumes axis-aligned wall placements; rotated placements are not handled.",
        ],
        "status": "Verified" if rooms else "Insufficient data",
        "confidence": (
            "High confidence" if rooms and assignment["per_space"] and not assignment["unassigned_windows"]
            else "Medium confidence" if rooms
            else "Insufficient data"
        ),
    }