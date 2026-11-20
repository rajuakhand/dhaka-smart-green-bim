"""
Unit tests for Module H — Structural Risk Screening.
"""
from src.modules.structural import screen_structural


class TestScreenStructural:
    def test_high_floor_building_flag(self):
        result = screen_structural(
            num_floors=8,
            construction_year=2020,
            structural_system="Frame",
        )
        flags = [f["flag_id"] for f in result["flags"]]
        assert "HEIGHT_SEISMIC" in flags

    def test_old_building_flag(self):
        result = screen_structural(
            num_floors=4,
            construction_year=2000,
            structural_system="Frame",
        )
        flags = [f["flag_id"] for f in result["flags"]]
        assert "AGE_DEGRADATION" in flags

    def test_missing_structural_system(self):
        result = screen_structural(
            num_floors=4,
            construction_year=2020,
            structural_system=None,
        )
        assert any("Structural system" in m for m in result["missing_information"])

    def test_missing_soil_info(self):
        result = screen_structural(
            num_floors=4,
            construction_year=2020,
            structural_system="Frame",
            soil_info_available=False,
        )
        assert any("soil" in m.lower() for m in result["missing_information"])

    def test_disclaimer_present(self):
        result = screen_structural(
            num_floors=4,
            construction_year=2020,
            structural_system="Frame",
        )
        assert "NOT a structural assessment" in result["disclaimer"]

    def test_confidence_insufficient(self):
        result = screen_structural(
            num_floors=4,
            construction_year=2020,
            structural_system="Frame",
        )
        assert "Insufficient" in result["confidence"]

    def test_status_needs_review_when_flags(self):
        result = screen_structural(
            num_floors=10,
            construction_year=2020,
            structural_system="Frame",
        )
        assert result["status"] == "Needs professional review"

    def test_no_false_safety_claim(self):
        result = screen_structural(
            num_floors=2,
            construction_year=2020,
            structural_system="Frame",
        )
        # Even a simple building must not claim safety
        assert "safe" not in result.get("status", "").lower()
        # The disclaimer contains "safety" which is correct (it says NOT safe)
        assert "not a structural" in result.get("disclaimer", "").lower()