"""
Module P2-7 — Local Material and Assembly Database (Bangladesh).

Provides U-values (W/m2K) and solar properties for typical Bangladeshi
construction assemblies, with each record carrying its source and verification
status.

Data provenance and honesty rules:
    - Every material record names its source (SRC id) and verification status.
    - Where a value is a typical/derived figure rather than a measured or
      published one, it is flagged "Estimated" and must not be reported as
      verified.
    - No value is silently invented: derived values are computed from
      layer thickness and published conductivity and are labelled as such.

Reference framework:
    - BNBC 2020 Part 3 Chapter 4 (Energy Efficiency & Sustainability) sets
      envelope performance intent but does not publish a full U-value table
      for every assembly.
    - ASHRAE Fundamentals / CIBSE Guide A typical values are used for the
      screening defaults and are explicitly marked as international defaults,
      not Bangladesh-specific measurements.
    - Brick is the dominant wall material in Dhaka; 150 mm brick with plaster
      is the reference baseline assembly (SRC-016 / BNBC Part 5 context).

U-value calculation for a multi-layer assembly (ISO 6946):
    U = 1 / (Rsi + sum(L_i / k_i) + Rse)
    Rsi = 0.13 m2K/W (internal surface resistance, horizontal heat flow)
    Rse = 0.04 m2K/W (external surface resistance)
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

# Surface resistances per ISO 6946 (horizontal heat flow)
RSI = 0.13
RSE = 0.04


@dataclass
class MaterialLayer:
    name: str
    thickness_mm: float
    conductivity_w_mk: float
    source_id: str
    verification: str = "Verified"
    notes: str = ""


@dataclass
class Assembly:
    assembly_id: str
    name: str
    category: str  # wall, roof, floor, glazing
    layers: list[MaterialLayer] = field(default_factory=list)
    u_value_w_m2k: float = 0.0
    source_id: str = ""
    verification: str = "Verified"
    notes: str = ""


def u_value_from_layers(layers: list[MaterialLayer]) -> float:
    """ISO 6946 U-value from layers: U = 1 / (Rsi + sum(L/k) + Rse)."""
    r_total = RSI + RSE
    for layer in layers:
        if layer.thickness_mm <= 0 or layer.conductivity_w_mk <= 0:
            continue
        r_total += (layer.thickness_mm / 1000.0) / layer.conductivity_w_mk
    if r_total <= 0:
        return 0.0
    return round(1.0 / r_total, 3)


# --- Reference assemblies for Dhaka residential construction ---
# Layer conductivities are typical published values for these materials
# (brick ~0.72, concrete ~1.65, plaster ~0.72, insulation ~0.04 W/mK).
# The U-value is DERIVED from layer thickness and conductivity, not measured.

WALL_150_BRICK_PLASTER = Assembly(
    assembly_id="WALL-BRICK-150",
    name="150 mm brick wall with 13 mm plaster both sides",
    category="wall",
    source_id="SRC-016",
    verification="Estimated (derived from typical conductivities)",
    notes=(
        "Reference Dhaka residential baseline. U-value derived from layer "
        "thickness and typical conductivities per ISO 6946; not a measured value."
    ),
    layers=[
        MaterialLayer("Internal plaster", 13, 0.72, "SRC-016", "Estimated"),
        MaterialLayer("Brick (150 mm)", 150, 0.72, "SRC-016", "Estimated"),
        MaterialLayer("External plaster", 13, 0.72, "SRC-016", "Estimated"),
    ],
)
WALL_150_BRICK_PLASTER.u_value_w_m2k = u_value_from_layers(WALL_150_BRICK_PLASTER.layers)

WALL_BRICK_INSULATED = Assembly(
    assembly_id="WALL-BRICK-INS",
    name="150 mm brick + 50 mm EPS insulation + plaster",
    category="wall",
    source_id="SRC-016",
    verification="Estimated (derived from typical conductivities)",
    notes="Improved envelope for hot-humid climate; U-value derived, not measured.",
    layers=[
        MaterialLayer("Internal plaster", 13, 0.72, "SRC-016", "Estimated"),
        MaterialLayer("Brick (150 mm)", 150, 0.72, "SRC-016", "Estimated"),
        MaterialLayer("EPS insulation (50 mm)", 50, 0.04, "SRC-016", "Estimated"),
        MaterialLayer("External plaster", 13, 0.72, "SRC-016", "Estimated"),
    ],
)
WALL_BRICK_INSULATED.u_value_w_m2k = u_value_from_layers(WALL_BRICK_INSULATED.layers)

ROOF_CONCRETE = Assembly(
    assembly_id="ROOF-CONCRETE-125",
    name="125 mm reinforced concrete roof slab",
    category="roof",
    source_id="SRC-016",
    verification="Estimated (derived from typical conductivities)",
    notes="Typical Dhaka flat RCC roof; U-value derived, not measured.",
    layers=[
        MaterialLayer("RCC slab (125 mm)", 125, 1.65, "SRC-016", "Estimated"),
    ],
)
ROOF_CONCRETE.u_value_w_m2k = u_value_from_layers(ROOF_CONCRETE.layers)

ROOF_CONCRETE_INSULATED = Assembly(
    assembly_id="ROOF-CONCRETE-INS",
    name="125 mm RCC + 50 mm XPS insulation",
    category="roof",
    source_id="SRC-016",
    verification="Estimated (derived from typical conductivities)",
    notes="Reduces roof solar gain; U-value derived, not measured.",
    layers=[
        MaterialLayer("RCC slab (125 mm)", 125, 1.65, "SRC-016", "Estimated"),
        MaterialLayer("XPS insulation (50 mm)", 50, 0.035, "SRC-016", "Estimated"),
    ],
)
ROOF_CONCRETE_INSULATED.u_value_w_m2k = u_value_from_layers(ROOF_CONCRETE_INSULATED.layers)

FLOOR_CONCRETE = Assembly(
    assembly_id="FLOOR-RCC-100",
    name="100 mm RCC floor slab on grade",
    category="floor",
    source_id="SRC-016",
    verification="Estimated (derived from typical conductivities)",
    notes="Ground-coupled floor; U-value derived, not measured.",
    layers=[
        MaterialLayer("RCC slab (100 mm)", 100, 1.65, "SRC-016", "Estimated"),
    ],
)
FLOOR_CONCRETE.u_value_w_m2k = u_value_from_layers(FLOOR_CONCRETE.layers)


# Glazing assemblies: U-value and SHGC by type.
# These are typical manufacturer-range values, flagged as screening defaults.
GLAZING_ASSEMBLIES: dict[str, dict] = {
    "Clear": {
        "assembly_id": "GLZ-CLEAR",
        "name": "Single clear float glazing (6 mm)",
        "category": "glazing",
        "u_value_w_m2k": 5.7,
        "shgc": 0.82,
        "vt": 0.85,
        "source_id": "SRC-016",
        "verification": "Estimated (typical manufacturer range)",
        "notes": "Single glazing typical of existing Dhaka stock (87% single glazing per BEEER survey).",
    },
    "Tinted": {
        "assembly_id": "GLZ-TINTED",
        "name": "Single tinted solar-control glazing (6 mm)",
        "category": "glazing",
        "u_value_w_m2k": 5.4,
        "shgc": 0.55,
        "vt": 0.55,
        "source_id": "SRC-016",
        "verification": "Estimated (typical manufacturer range)",
        "notes": "Reduces solar gain but also visible transmittance.",
    },
    "Double low-E": {
        "assembly_id": "GLZ-DLOW-E",
        "name": "Double glazed with low-E coating (6-12-6 mm)",
        "category": "glazing",
        "u_value_w_m2k": 1.8,
        "shgc": 0.35,
        "vt": 0.72,
        "source_id": "SRC-016",
        "verification": "Estimated (typical manufacturer range)",
        "notes": "Best available option for hot-humid climate; higher cost.",
    },
}


def list_assemblies() -> dict:
    """Return all assemblies grouped by category."""
    assemblies = [
        WALL_150_BRICK_PLASTER,
        WALL_BRICK_INSULATED,
        ROOF_CONCRETE,
        ROOF_CONCRETE_INSULATED,
        FLOOR_CONCRETE,
    ]
    return {
        "opaque": {
            "unit": "W/m2K",
            "method": "ISO 6946 derived from layer thickness and conductivity",
            "assemblies": [asdict(a) for a in assemblies],
        },
        "glazing": {
            "unit": "U: W/m2K; SHGC and VT dimensionless",
            "method": "typical manufacturer ranges (screening defaults)",
            "assemblies": list(GLAZING_ASSEMBLIES.values()),
        },
        "surface_resistances": {"Rsi_m2k_w": RSI, "Rse_m2k_w": RSE},
        "limitations": [
            "All U-values are DERIVED from layer thickness and typical conductivities, not measured.",
            "No Bangladesh-specific laboratory test data is available in this database.",
            "Weather/temperature dependence of U-value is not modelled.",
            "Thermal bridging at junctions is not included.",
        ],
    }


def get_assembly(assembly_id: str) -> dict | None:
    """Look up an assembly by id (opaque or glazing).

    Accepts either an opaque assembly_id (e.g. 'WALL-BRICK-150'), a glazing
    type key (e.g. 'Clear'), or a glazing assembly_id (e.g. 'GLZ-CLEAR').
    """
    for a in [
        WALL_150_BRICK_PLASTER,
        WALL_BRICK_INSULATED,
        ROOF_CONCRETE,
        ROOF_CONCRETE_INSULATED,
        FLOOR_CONCRETE,
    ]:
        if a.assembly_id == assembly_id:
            return asdict(a)

    # Glazing: match by type key or by assembly_id
    if assembly_id in GLAZING_ASSEMBLIES:
        return GLAZING_ASSEMBLIES[assembly_id]
    for g in GLAZING_ASSEMBLIES.values():
        if g["assembly_id"] == assembly_id:
            return g
    return None


def envelope_summary(
    wall_assembly_id: str = "WALL-BRICK-150",
    roof_assembly_id: str = "ROOF-CONCRETE-125",
    glazing_type: str = "Clear",
    wall_area_m2: float = 0.0,
    roof_area_m2: float = 0.0,
    glazing_area_m2: float = 0.0,
) -> dict:
    """Summarise an envelope and compute an area-weighted assembly U-value."""
    wall = get_assembly(wall_assembly_id)
    roof = get_assembly(roof_assembly_id)
    glazing = GLAZING_ASSEMBLIES.get(glazing_type)
    if wall is None or roof is None or glazing is None:
        return {"status": "Insufficient data", "error": "Unknown assembly id."}

    total_area = wall_area_m2 + roof_area_m2 + glazing_area_m2
    if total_area <= 0:
        return {
            "status": "Insufficient data",
            "error": "Envelope areas are zero; cannot compute a weighted U-value.",
            "wall": wall,
            "roof": roof,
            "glazing": glazing,
        }

    weighted = (
        (wall.get("u_value_w_m2k", 0.0) or 0.0) * wall_area_m2
        + (roof.get("u_value_w_m2k", 0.0) or 0.0) * roof_area_m2
        + (glazing.get("u_value_w_m2k", 0.0) or 0.0) * glazing_area_m2
    ) / total_area

    return {
        "status": "Estimated",
        "wall": wall,
        "roof": roof,
        "glazing": glazing,
        "areas_m2": {
            "wall": wall_area_m2,
            "roof": roof_area_m2,
            "glazing": glazing_area_m2,
            "total": round(total_area, 2),
        },
        "area_weighted_u_value_w_m2k": round(weighted, 3),
        "glazing_fraction_percent": round(
            (glazing_area_m2 / total_area) * 100.0, 1
        ) if total_area > 0 else 0.0,
        "method": "area-weighted average of assembly U-values",
        "limitations": [
            "U-values are derived, not measured (ISO 6946 from typical conductivities).",
            "Thermal bridging and air infiltration are excluded.",
            "Area-weighted average masks the performance of individual elements.",
        ],
    }