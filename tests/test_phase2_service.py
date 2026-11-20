"""
Phase 2 tests — Simulation bridge and full Phase 2 orchestration.

The bridge tests are critical: they verify that the platform never claims a
simulation ran when it did not.
"""
import pytest

from src.models.schemas import BuildingCreate, RoomCreate, BuildingType, RoomType
from src.modules.simulation_bridge import (
    detect_energyplus,
    detect_radiance,
    not_evaluated,
    require_engine,
    simulation_capability_report,
)
from src.services.phase2_service import PHASE2_DISCLAIMER, run_phase2_analysis


class TestEngineDetection:
    def test_energyplus_returns_status_object(self):
        s = detect_energyplus()
        assert isinstance(s.available, bool)
        assert s.name == "EnergyPlus"
        assert s.detection_method

    def test_radiance_returns_status_object(self):
        s = detect_radiance()
        assert isinstance(s.available, bool)
        assert s.name == "Radiance"

    def test_unsupported_engine_is_unavailable(self):
        s = require_engine("OpenFOAM")
        assert s.available is False
        assert "unsupported" in s.detection_method.lower()

    def test_detection_never_raises(self):
        """Engine detection must not crash even in a broken environment."""
        assert detect_energyplus().available in (True, False)
        assert detect_radiance().available in (True, False)


class TestCapabilityReport:
    def test_report_structure(self):
        r = simulation_capability_report()
        assert "energyplus" in r["engines"]
        assert "radiance" in r["engines"]
        assert isinstance(r["any_engine_available"], bool)

    def test_reports_no_fabrication_principle(self):
        r = simulation_capability_report()
        assert "never report simulated" in r["principle"].lower()

    def test_engine_status_fields(self):
        r = simulation_capability_report()
        ep = r["engines"]["energyplus"]
        for field in ("name", "available", "path", "version", "detection_method", "install_hint"):
            assert field in ep


class TestNotEvaluated:
    def test_marks_executed_false(self):
        """CRITICAL: a missing engine must never be reported as executed."""
        r = not_evaluated("EnergyPlus")
        assert r["executed"] is False
        assert r["simulated"] is False

    def test_status_is_not_evaluated(self):
        r = not_evaluated("EnergyPlus")
        assert r["status"] == "Not evaluated"

    def test_confidence_is_insufficient(self):
        r = not_evaluated("EnergyPlus")
        assert "Insufficient" in r["confidence"]

    def test_no_numeric_result_present(self):
        """Must not invent a plausible-looking number."""
        r = not_evaluated("EnergyPlus")
        assert "result" not in r
        assert "value" not in r

    def test_limitations_explain_why(self):
        r = not_evaluated("Radiance")
        assert len(r["limitations"]) > 0
        assert any("no number" in l.lower() for l in r["limitations"])


# --------------------------------------------------------------------------
# Full Phase 2 orchestration
# --------------------------------------------------------------------------

def _fixture():
    building = BuildingCreate(
        name="Dhaka Residential Block A",
        building_type=BuildingType.RESIDENTIAL,
        num_floors=6,
        floor_to_floor_height_m=3.0,
        orientation_deg=180.0,
        plot_area_m2=500.0,
        building_footprint_m2=200.0,
    )
    rooms = [
        RoomCreate(name="Living Room", room_type=RoomType.RESIDENTIAL,
                   length_m=5, width_m=4, height_m=3, occupants=4,
                   window_area_m2=4, openable_window_area_m2=2),
        RoomCreate(name="Bedroom 1", room_type=RoomType.RESIDENTIAL,
                   length_m=4, width_m=3, height_m=3, occupants=2,
                   window_area_m2=3, openable_window_area_m2=1.5),
    ]
    return building, rooms


class TestPhase2Orchestration:
    def test_returns_all_modules(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        for key in ("climate", "solar_geometry", "daylight_factor", "shading",
                    "materials", "envelope", "sensitivity", "optimization",
                    "simulation_engines"):
            assert key in r["modules"], f"missing module: {key}"

    def test_includes_disclaimer(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        assert "NOT" in r["disclaimer"]
        assert "simulation" in r["disclaimer"].lower()

    def test_simulation_status_honest(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        # Regardless of engine availability, the report must state no execution
        assert r["simulation_status"]["energyplus_executed"] is False
        assert r["simulation_status"]["radiance_executed"] is False

    def test_climate_has_source_provenance(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        ds = r["modules"]["climate"]["dataset"]
        assert ds["dataset_id"]
        assert ds["source_name"]
        assert ds["period"]

    def test_daylight_per_room(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        results = r["modules"]["daylight_factor"]["rooms"]
        assert len(results) == 2
        for d in results:
            assert d["room_name"]
            assert "daylight_factor_percent" in d or "message" in d

    def test_sensitivity_ranks_parameters(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        sens = r["modules"]["sensitivity"]
        assert sens["parameters_tested"] == 4
        assert sens["most_influential"] == "ac_cop"
        assert len(sens["ranking_by_influence"]) == 4

    def test_optimization_finds_improvement(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        opt = r["modules"]["optimization"]
        assert opt["evaluated"] > 0
        assert opt["best"]["design"]["ac_cop"] == 4.0

    def test_orientation_used_in_solar(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        fs = r["modules"]["solar_geometry"]["facade_solar"]
        assert fs["facades"]["Front"]["azimuth_deg"] == 180.0

    def test_source_references_present(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        assert any("NASA POWER" in s for s in r["source_references"])
        assert any("ISO 6946" in s for s in r["source_references"])

    def test_no_repeated_nasa_fetch_on_cache(self):
        """Running twice should hit the local cache and still succeed."""
        b, rooms = _fixture()
        r1 = run_phase2_analysis(b, rooms)
        r2 = run_phase2_analysis(b, rooms)
        assert r1["modules"]["climate"]["dataset"]["dataset_id"] == \
               r2["modules"]["climate"]["dataset"]["dataset_id"]

    def test_overall_confidence_present(self):
        b, rooms = _fixture()
        r = run_phase2_analysis(b, rooms)
        assert r["overall_confidence"] in (
            "High confidence", "Medium confidence", "Low confidence", "Insufficient data"
        )