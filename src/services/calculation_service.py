"""
Calculation service.

Orchestrates all deterministic calculation modules and assembles the
full result envelope with provenance metadata.
"""
from __future__ import annotations

from datetime import datetime, timezone

from src.models.schemas import (
    BuildingCreate,
    CalculationEnvelope,
    RoomCreate,
    ConfidenceLevel,
)
from src.modules.building_setup import validate_building
from src.modules.room_analyzer import analyze_rooms
from src.modules.ventilation import screen_all_rooms
from src.modules.daylight import screen_all_rooms_daylight
from src.modules.energy import estimate_building_energy
from src.modules.carbon import calculate_carbon
from src.modules.density import calculate_density
from src.modules.structural import screen_structural
from src.modules.optimization import compare_energy_cases
from src.modules.phase2_advanced import EnergyPlusIntegration, DaylightAdvanced, AdvancedShading, SensitivityAnalysis
from src.modules.phase3_bim import IFCImporter, BIMGeometryExtractor, GeometryValidator, IFCToAnalysisModel

# Source references for the full calculation set
SOURCE_REFERENCES = [
    "SRC-001: BNBC 2020 (Occupancy, Ventilation, Daylight)",
    "SRC-002: RAJUK DAP 2022-2035 (FAR, coverage, open space)",
    "SRC-006: DoE Grid Emission Factor 2019-22",
    "SRC-008: Ember/OWID Electricity Carbon Intensity 2025",
    "SRC-010: EnergyPlus EPW (Dhaka SWERA 419230)",
    "SRC-013: Chaudhary & Akhtar 2023 (ICMD factors, India)",
    "SRC-014: GlobalABC Bangladesh Buildings Roadmap 2025",
]

DISCLAIMER = (
    "This is a PRELIMINARY analysis. Results are screening-level estimates "
    "with documented assumptions and limitations. They are NOT a substitute "
    "for verified structural assessment, certified energy simulation, "
    "professional engineering review, or regulatory compliance certification. "
    "Always engage qualified professionals for design decisions."
)


def run_full_analysis(
    building: BuildingCreate,
    rooms: list[RoomCreate],
    *,
    ac_cop: float = 3.1,
    cooling_hours: float = 1800.0,
    lighting_hours: float = 2500.0,
    equipment_hours: float = 2500.0,
    emission_factor_source: str = "DoE-GEF",
    rajuk_zone: str | None = None,
    alternatives: list[dict] | None = None,
) -> CalculationEnvelope:
    """Run all calculation modules and return a full result envelope."""

    # Module A
    building_ctx = validate_building(building)

    # Module B
    room_analysis = analyze_rooms(rooms)
    total_floor_area = room_analysis["summary"]["total_floor_area_m2"]
    total_occupants = room_analysis["summary"]["total_occupants"]

    # Module C
    ventilation = screen_all_rooms(rooms)

    # Module D
    daylight = screen_all_rooms_daylight(rooms)

    # Module E
    energy = estimate_building_energy(
        rooms,
        ac_cop=ac_cop,
        cooling_hours=cooling_hours,
        lighting_hours=lighting_hours,
        equipment_hours=equipment_hours,
    )

    # Module F
    carbon = calculate_carbon(
        electricity_kwh_per_year=energy["total_electricity_kwh_per_year"],
        emission_factor_source=emission_factor_source,
    )

    # Module G
    density = calculate_density(
        total_floor_area_m2=total_floor_area,
        plot_area_m2=building.plot_area_m2,
        footprint_m2=building.building_footprint_m2,
        total_occupants=total_occupants,
        rajuk_zone=rajuk_zone,
    )

    # Module H
    structural = screen_structural(
        num_floors=building.num_floors,
        construction_year=building.construction_year,
        structural_system=(
            building.structural_system.value if building.structural_system else None
        ),
    )

    # Module I
    optimization = compare_energy_cases(
        rooms=rooms,
        baseline_assumptions={
            "ac_cop": ac_cop,
            "cooling_hours": cooling_hours,
            "lighting_hours": lighting_hours,
            "equipment_hours": equipment_hours,
        },
        alternatives=alternatives or [],
    )

    # Phase 2 modules (placeholders)
    phase2_energy = EnergyPlusIntegration.run_energy_simulation(
        building_id=getattr(building, "id", None) or "preview",
        rooms=rooms,
        epw_path="data/weather/Dhaka_419230.epw",
    )
    phase2_daylight = DaylightAdvanced.calculate_sda(
        room_geometry={},
        epw_path="data/weather/Dhaka_419230.epw",
        materials={},
    )
    phase2_shading = AdvancedShading.analyze_shading(
        room_geometry={},
        surrounding_buildings=[],
        sun_path={},
    )
    phase2_sensitivity = SensitivityAnalysis.run_sensitivity(
        baseline_inputs={},
        parameters=[],
    )

    # Phase 3 modules (placeholders)
    phase3_ifc = IFCToAnalysisModel.convert_to_analysis_model(
        ifc_path="",
        target_format="json",
    )
    phase3_geometry = GeometryValidator.validate_geometry({})
    phase3_spaces = BIMGeometryExtractor.extract_spaces("")

    # Overall confidence
    confidences = [
        building_ctx.get("confidence", ConfidenceLevel.MEDIUM.value),
        room_analysis["overall_confidence"],
        ventilation["confidence"],
        daylight["confidence"],
        energy["confidence"],
        carbon["confidence"],
        density["confidence"],
        structural["confidence"],
    ]
    high_count = sum(1 for c in confidences if "High" in c)
    if high_count >= len(confidences) - 2:
        overall = ConfidenceLevel.MEDIUM.value
    else:
        overall = ConfidenceLevel.LOW.value

    # Normalise the id to a plain string: persisted buildings carry a UUID,
    # preview buildings have none. Coerce explicitly so Pydantic never sees a
    # UUID object where a str is declared.
    raw_id = getattr(building, "id", None)
    project_id = str(raw_id) if raw_id is not None else "preview"

    return CalculationEnvelope(
        project_id=project_id,
        calculated_at=datetime.now(timezone.utc),
        modules={
            "A_building": building_ctx,
            "B_rooms": room_analysis,
            "C_ventilation": ventilation,
            "D_daylight": daylight,
            "E_energy": energy,
            "F_carbon": carbon,
            "G_density": density,
            "H_structural": structural,
            "I_optimization": optimization,
            "P2_energy_simulation": phase2_energy,
            "P2_daylight_advanced": phase2_daylight,
            "P2_shading_analysis": phase2_shading,
            "P2_sensitivity": phase2_sensitivity,
            "P3_ifc_conversion": phase3_ifc,
            "P3_geometry_validation": phase3_geometry,
            "P3_space_extraction": phase3_spaces,
        },
        source_references=SOURCE_REFERENCES,
        overall_confidence=overall,
        disclaimer=DISCLAIMER,
    )