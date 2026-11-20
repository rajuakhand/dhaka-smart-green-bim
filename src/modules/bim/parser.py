"""
Phase 3 — IFC Parsing and Model Extraction.

Parses an IFC file into a normalised Python model:

   IfcModel
      ├── schema            (IFC2X3 / IFC4 / IFC4X3)
      ├── length_unit       ('METRE' | 'MILLI' | 'CENTI' | ...)
      ├── length_scale      (factor to convert stored coords -> metres)
      ├── storeys[]
      ├── spaces[]          (IfcSpace -> room candidates)
      ├── walls[]           (IfcWall / IfcWallStandardCase)
      ├── slabs[]           (IfcSlab)
      ├── roofs[]           (IfcRoof)
      ├── windows[]         (IfcWindow)
      ├── doors[]           (IfcDoor)
      └── warnings[]

UNIT HANDLING (critical, documented):
    IFC length values are expressed in the file's length unit. Most BIM exports
    use MILLIMETRE. Reading coordinates without scaling by 1000 is the single
    most common IFC bug and produces rooms 1000x too small. This parser reads
    IfcUnitAssignment and returns an explicit `length_scale`, and every linear
    dimension in the output is in METRES.

GEOMETRY EXTRACTION (documented scope):
    Supports IFC4/IFC2X3 `IfcExtrudedAreaSolid` with a rectangular or
    arbitrary-closed profile — the representation produced by the vast majority
    of architectural exporters for walls, slabs and spaces.

    For each element we compute:
        volume_m3   = profile_area_m2 * depth_m        (always, rectangular profile)
        bbox_x/y/z  = XDim, YDim, Depth                (local axes, before placement)
        footprint_m2 = XDim * YDim                     (plan projection)
        elevation_m2 = XDim * Depth                    (for walls)

    B-rep / faceted / CSG geometry is NOT evaluated and is reported as a
    limitation rather than approximated.

LIMITATIONS (always surfaced):
    - No window-to-wall relationship resolution unless IfcRelFillsElement /
      IfcRelVoidsElement are present.
    - No material / thermal property extraction in this module (Phase 3 scope).
    - Element connectivity (which wall bounds which space) is not derived.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from src.core.exceptions import ValidationFailure
from src.modules.bim.engine import detect_ifc_engine

# IFC length unit prefixes -> multiplier to metres
IFC_LENGTH_PREFIX_TO_METRES = {
    None: 1.0,        # plain METRE
    "EXA": 1e18,
    "PETA": 1e15,
    "TERA": 1e12,
    "GIGA": 1e9,
    "MEGA": 1e6,
    "KILO": 1e3,
    "HECTO": 1e2,
    "DECA": 1e1,
    "DECI": 1e-1,
    "CENTI": 1e-2,
    "MILLI": 1e-3,
    "MICRO": 1e-6,
    "NANO": 1e-9,
}

# Entity types treated as rooms/spaces
SPACE_TYPES = {"IfcSpace", "IfcZone", "IfcSpatialZone"}

# Entity types treated as opaque vertical envelope
WALL_TYPES = {"IfcWall", "IfcWallStandardCase", "IfcCurtainWall"}

# Entity types treated as horizontal opaque envelope
SLAB_TYPES = {"IfcSlab", "IfcCovering"}
ROOF_TYPES = {"IfcRoof", "IfcRoofType"}

# Entity types treated as openings
WINDOW_TYPES = {"IfcWindow", "IfcWindowStandardCase"}
DOOR_TYPES = {"IfcDoor", "IfcDoorStandardCase"}

# Entity types that produce a swept solid we can measure
EXTRUSION_TYPE = "IfcExtrudedAreaSolid"


@dataclass
class IfcElement:
    """A single extracted element with metre-based geometry."""

    entity_type: str
    global_id: str
    name: Optional[str]
    storey: Optional[str]
    # local-axis dimensions in METRES
    x_dim_m: float = 0.0
    y_dim_m: float = 0.0
    z_dim_m: float = 0.0
    volume_m3: float = 0.0
    footprint_m2: float = 0.0
    elevation_m2: float = 0.0
    # placement origin in METRES (model coordinates)
    origin_m: tuple[float, float, float] = (0.0, 0.0, 0.0)
    # explicit opening sizes (IfcWindow / IfcDoor attributes)
    overall_width_m: Optional[float] = None
    overall_height_m: Optional[float] = None
    has_measurable_geometry: bool = False
    geometry_note: str = ""


@dataclass
class IfcModel:
    """Normalised IFC model in metre units."""

    file_path: str
    file_size_bytes: int
    schema: str
    length_unit: str
    length_scale: float
    project_name: Optional[str] = None
    site_name: Optional[str] = None
    building_name: Optional[str] = None
    storeys: list[str] = field(default_factory=list)
    spaces: list[IfcElement] = field(default_factory=list)
    walls: list[IfcElement] = field(default_factory=list)
    slabs: list[IfcElement] = field(default_factory=list)
    roofs: list[IfcElement] = field(default_factory=list)
    windows: list[IfcElement] = field(default_factory=list)
    doors: list[IfcElement] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unsupported_geometry: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def total_floor_area_m2(self) -> float:
        return round(sum(s.footprint_m2 for s in self.spaces), 3)

    @property
    def total_envelope_area_m2(self) -> float:
        return round(
            sum(w.elevation_m2 for w in self.walls)
            + sum(s.footprint_m2 for s in self.slabs)
            + sum(r.footprint_m2 for r in self.roofs),
            3,
        )

    @property
    def total_window_area_m2(self) -> float:
        return round(
            sum(
                (w.overall_width_m or 0.0) * (w.overall_height_m or 0.0)
                for w in self.windows
            ),
            3,
        )

    @property
    def element_counts(self) -> dict[str, int]:
        return {
            "spaces": len(self.spaces),
            "walls": len(self.walls),
            "slabs": len(self.slabs),
            "roofs": len(self.roofs),
            "windows": len(self.windows),
            "doors": len(self.doors),
            "storeys": len(self.storeys),
        }


def _check_engine():
    status = detect_ifc_engine()
    if not status.available:
        raise ValidationFailure(
            "IfcOpenShell is not available, so the IFC file cannot be parsed. "
            f"{status.install_hint or status.error}"
        )
    import ifcopenshell  # noqa: F401 - re-import after successful detection
    return ifcopenshell


def _length_scale(ifc_file) -> tuple[str, float, Optional[str]]:
    """Read the file's length unit and return (unit_label, scale_to_metres, note)."""
    try:
        for assignment in ifc_file.by_type("IfcUnitAssignment"):
            for unit in assignment.Units:
                if not unit.is_a("IfcSIUnit"):
                    continue
                if unit.UnitType != "LENGTHUNIT":
                    continue
                prefix = getattr(unit, "Prefix", None)
                name = getattr(unit, "Name", None)
                if name and name not in ("METRE",):
                    # Non-SI length unit (e.g. FOOT) - we do not guess
                    return name, 1.0, (
                        f"Non-SI length unit '{name}' is not converted; "
                        "dimensions are assumed to be metres."
                    )
                scale = IFC_LENGTH_PREFIX_TO_METRES.get(prefix, 1.0)
                label = f"{prefix} {name}".strip() if prefix else (name or "METRE")
                return label, scale, None
    except Exception:  # noqa: BLE001
        pass
    return "METRE (assumed)", 1.0, (
        "No IfcUnitAssignment found; length unit assumed to be metres."
    )


def _placement_origin(element) -> tuple[float, float, float]:
    """Extract the local placement origin (model coords, pre-scale)."""
    try:
        placement = getattr(element, "ObjectPlacement", None)
        if placement is None:
            return (0.0, 0.0, 0.0)
        rel = getattr(placement, "RelativePlacement", None)
        if rel is None:
            return (0.0, 0.0, 0.0)
        loc = getattr(rel, "Location", None)
        if loc is None:
            return (0.0, 0.0, 0.0)
        coords = getattr(loc, "Coordinates", None)
        if not coords:
            return (0.0, 0.0, 0.0)
        return (float(coords[0]), float(coords[1]), float(coords[2]))
    except Exception:  # noqa: BLE001
        return (0.0, 0.0, 0.0)


def _storey_of(ifc_file, element) -> Optional[str]:
    """Resolve the containing IfcBuildingStorey name for an element."""
    try:
        for rel in ifc_file.get_inverse(element):
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                structure = getattr(rel, "RelatingStructure", None)
                if structure is not None:
                    return getattr(structure, "Name", None)
    except Exception:  # noqa: BLE001
        pass
    return None


def _measure_extrusion(item) -> Optional[dict]:
    """Measure an IfcExtrudedAreaSolid. Returns None if unsupported."""
    if not item.is_a(EXTRUSION_TYPE):
        return None

    swept = getattr(item, "SweptArea", None)
    depth = getattr(item, "Depth", None)
    if depth is None:
        return None
    depth = float(depth)

    x_dim = y_dim = None
    profile_kind = None

    if swept is not None and swept.is_a("IfcRectangleProfileDef"):
        x_dim = float(getattr(swept, "XDim", 0.0) or 0.0)
        y_dim = float(getattr(swept, "YDim", 0.0) or 0.0)
        profile_kind = "rectangle"
    elif swept is not None and swept.is_a("IfcCircleProfileDef"):
        radius = float(getattr(swept, "Radius", 0.0) or 0.0)
        x_dim = y_dim = 2.0 * radius
        profile_kind = "circle"
    elif swept is not None and swept.is_a("IfcArbitraryClosedProfileDef"):
        # Approximate from the outer curve's bounding box when available
        outer = getattr(swept, "OuterCurve", None)
        pts = getattr(outer, "Points", None) if outer is not None else None
        if pts:
            xs = [float(p.Coordinates[0]) for p in pts if p.Coordinates]
            ys = [float(p.Coordinates[1]) for p in pts if p.Coordinates]
            if xs and ys:
                x_dim = max(xs) - min(xs)
                y_dim = max(ys) - min(ys)
                profile_kind = "arbitrary_bbox"
    else:
        return None

    if x_dim is None or y_dim is None:
        return None

    profile_area = x_dim * y_dim
    volume = profile_area * depth
    return {
        "x_dim": x_dim,
        "y_dim": y_dim,
        "z_dim": depth,
        "profile_area": profile_area,
        "volume": volume,
        "footprint": x_dim * y_dim,
        "elevation": x_dim * depth,
        "profile_kind": profile_kind,
    }


def _measure_element(ifc_file, element) -> IfcElement:
    """Build an IfcElement with metre-scaled geometry for one entity."""
    scale = ifc_file._dhaka_length_scale  # type: ignore[attr-defined]
    origin_raw = _placement_origin(element)
    origin = tuple(round(c * scale, 6) for c in origin_raw)
    entity_type = element.is_a()

    out = IfcElement(
        entity_type=entity_type,
        global_id=getattr(element, "GlobalId", "") or "",
        name=getattr(element, "Name", None),
        storey=_storey_of(ifc_file, element),
        origin_m=origin,  # type: ignore[arg-type]
    )

    # Explicit opening dimensions (IfcWindow / IfcDoor attributes)
    if entity_type in ("IfcWindow", "IfcWindowStandardCase",
                       "IfcDoor", "IfcDoorStandardCase"):
        w = getattr(element, "OverallWidth", None)
        h = getattr(element, "OverallHeight", None)
        if w is not None:
            out.overall_width_m = round(float(w) * scale, 4)
        if h is not None:
            out.overall_height_m = round(float(h) * scale, 4)

    # Representation geometry
    shape = getattr(element, "Representation", None)
    if shape is not None:
        try:
            for rep in getattr(shape, "Representations", []) or []:
                for item in getattr(rep, "Items", []) or []:
                    m = _measure_extrusion(item)
                    if m is None:
                        continue
                    out.x_dim_m = round(m["x_dim"] * scale, 4)
                    out.y_dim_m = round(m["y_dim"] * scale, 4)
                    out.z_dim_m = round(m["z_dim"] * scale, 4)
                    out.volume_m3 = round(m["volume"] * (scale ** 3), 4)
                    out.footprint_m2 = round(m["footprint"] * (scale ** 2), 4)
                    out.elevation_m2 = round(
                        _elevation_for(entity_type, m) * (scale ** 2), 4
                    )
                    out.has_measurable_geometry = True
                    out.geometry_note = m["profile_kind"]
                    return out
        except Exception as exc:  # noqa: BLE001
            out.geometry_note = f"representation read error: {exc}"

    out.geometry_note = out.geometry_note or "no supported swept-solid representation"
    return out


# Entity types whose extrusion depth is the VERTICAL dimension (wall height).
# For these the visible face area is plan-length x height, not profile-X x depth.
_VERTICAL_ELEMENT_TYPES = {
    "IfcWall", "IfcWallStandardCase", "IfcCurtainWall",
    "IfcWindow", "IfcWindowStandardCase",
    "IfcDoor", "IfcDoorStandardCase",
}


def _elevation_for(entity_type: str, m: dict) -> float:
    """Vertical face area for an element.

    For a vertical element (wall) modelled as a rectangle profile extruded
    upwards, the profile's longer side is the wall length and the shorter side
    is the thickness. The visible elevation is length x height.

    Example: a 0.23 x 4.0 m profile extruded 3.0 m -> elevation = 4.0 x 3.0 = 12,
    NOT 0.23 x 3.0 = 0.69.
    """
    x = m["x_dim"]
    y = m["y_dim"]
    depth = m["z_dim"]
    if entity_type in _VERTICAL_ELEMENT_TYPES:
        plan_length = max(x, y)
        return plan_length * depth
    return m["elevation"]


def _collect(ifc_file, types: set[str]) -> list[IfcElement]:
    """Collect and measure all entities whose type is in `types`."""
    result: list[IfcElement] = []
    for entity_type in types:
        try:
            for element in ifc_file.by_type(entity_type):
                result.append(_measure_element(ifc_file, element))
        except Exception:  # noqa: BLE001 - unknown type in older schemas
            continue
    return result


def parse_ifc(file_path: str) -> IfcModel:
    """Parse an IFC file into a normalised, metre-based model.

    Raises:
        ValidationFailure: file missing, wrong type, or IfcOpenShell unavailable.
    """
    ifcopenshell = _check_engine()

    # Validate the extension first: it is a cheaper, clearer error than
    # "file not found" for an obviously wrong upload.
    if not file_path.lower().endswith(".ifc"):
        raise ValidationFailure(
            f"Unsupported file type. Only .ifc files are supported "
            f"(got '{os.path.splitext(file_path)[1] or 'no extension'}')."
        )
    if not os.path.exists(file_path):
        raise ValidationFailure(f"IFC file not found: {file_path}")
    size = os.path.getsize(file_path)
    if size == 0:
        raise ValidationFailure("IFC file is empty.")

    try:
        ifc_file = ifcopenshell.open(file_path)
    except Exception as exc:  # noqa: BLE001
        raise ValidationFailure(f"IfcOpenShell could not open the file: {exc}")

    if ifc_file is None:
        raise ValidationFailure("IfcOpenShell returned no model for this file.")

    label, scale, note = _length_scale(ifc_file)
    # stash the scale on the file object for _measure_element
    try:
        ifc_file._dhaka_length_scale = scale  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

    model = IfcModel(
        file_path=file_path,
        file_size_bytes=size,
        schema=ifc_file.schema,
        length_unit=label,
        length_scale=scale,
    )

    if note:
        model.warnings.append(note)
    if scale != 1.0:
        model.warnings.append(
            f"All linear dimensions were converted from {label} to metres "
            f"using a factor of {scale}."
        )

    # Names
    for project in ifc_file.by_type("IfcProject"):
        model.project_name = getattr(project, "Name", None)
        break
    for site in ifc_file.by_type("IfcSite"):
        model.site_name = getattr(site, "Name", None)
        break
    for building in ifc_file.by_type("IfcBuilding"):
        model.building_name = getattr(building, "Name", None)
        break

    # Storeys
    for storey in ifc_file.by_type("IfcBuildingStorey"):
        nm = getattr(storey, "Name", None)
        if nm:
            model.storeys.append(nm)

    model.spaces = _collect(ifc_file, SPACE_TYPES)
    model.walls = _collect(ifc_file, WALL_TYPES)
    model.slabs = _collect(ifc_file, SLAB_TYPES)
    model.roofs = _collect(ifc_file, ROOF_TYPES)
    model.windows = _collect(ifc_file, WINDOW_TYPES)
    model.doors = _collect(ifc_file, DOOR_TYPES)

    # Track unsupported geometry
    for group_name, group in [
        ("spaces", model.spaces), ("walls", model.walls), ("slabs", model.slabs),
        ("roofs", model.roofs), ("windows", model.windows), ("doors", model.doors),
    ]:
        for el in group:
            if not el.has_measurable_geometry and el.overall_width_m is None:
                model.unsupported_geometry.append(
                    f"{el.entity_type} '{el.name or el.global_id}' ({group_name}): "
                    f"{el.geometry_note}"
                )

    if not model.spaces:
        model.warnings.append(
            "No IfcSpace entities found; room-level analysis cannot be derived."
        )
    if not model.walls:
        model.warnings.append(
            "No IfcWall entities found; envelope analysis is limited."
        )

    return model


def model_summary(model: IfcModel) -> dict:
    """Compact summary for API/UI consumption."""
    return {
        "file": {
            "name": os.path.basename(model.file_path),
            "size_bytes": model.file_size_bytes,
            "schema": model.schema,
        },
        "units": {
            "length_unit": model.length_unit,
            "length_scale_to_metres": model.length_scale,
            "note": (
                "All reported dimensions are in metres."
                if model.length_scale == 1.0
                else f"Converted from {model.length_unit} to metres."
            ),
        },
        "hierarchy": {
            "project": model.project_name,
            "site": model.site_name,
            "building": model.building_name,
            "storeys": model.storeys,
        },
        "counts": model.element_counts,
        "areas": {
            "total_space_floor_area_m2": model.total_floor_area_m2,
            "total_envelope_area_m2": model.total_envelope_area_m2,
            "total_window_area_m2": model.total_window_area_m2,
        },
        "warnings": model.warnings,
        "unsupported_geometry_count": len(model.unsupported_geometry),
        "unsupported_geometry_sample": model.unsupported_geometry[:10],
        "limitations": [
            "Only IfcExtrudedAreaSolid swept geometry is measured.",
            "B-rep, faceted and CSG geometry is reported as unsupported, not approximated.",
            "Space-to-wall connectivity is not derived in this module.",
            "No material or thermal properties are extracted here.",
        ],
        "status": "Verified" if model.spaces or model.walls else "Insufficient data",
        "confidence": "High confidence" if model.spaces and model.walls else "Low confidence",
    }