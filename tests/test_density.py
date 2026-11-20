"""
Unit tests for Module G — Density and Urban Context.
"""
from src.modules.density import calculate_density, calculate_far, calculate_ground_coverage, calculate_open_space


class TestCalculateFAR:
    def test_basic_far(self):
        far = calculate_far(2400.0, 1000.0)
        assert far == 2.4

    def test_far_none_when_missing(self):
        assert calculate_far(None, 1000.0) is None
        assert calculate_far(2400.0, None) is None
        assert calculate_far(2400.0, 0) is None

    def test_far_boundary(self):
        far = calculate_far(1000.0, 1000.0)
        assert far == 1.0


class TestCalculateCoverage:
    def test_basic_coverage(self):
        cov = calculate_ground_coverage(500.0, 1000.0)
        assert cov == 50.0

    def test_coverage_none_when_missing(self):
        assert calculate_ground_coverage(None, 1000.0) is None

    def test_zero_coverage(self):
        cov = calculate_ground_coverage(0.0, 1000.0)
        assert cov == 0.0


class TestCalculateOpenSpace:
    def test_basic_open_space(self):
        os = calculate_open_space(500.0, 1000.0)
        assert os == 50.0

    def test_open_space_none_when_missing(self):
        assert calculate_open_space(None, 1000.0) is None

    def test_full_building_no_open_space(self):
        os = calculate_open_space(1000.0, 1000.0)
        assert os == 0.0


class TestCalculateDensity:
    def test_full_density(self):
        result = calculate_density(
            total_floor_area_m2=2400.0,
            plot_area_m2=1000.0,
            footprint_m2=500.0,
            total_occupants=20,
            rajuk_zone="Mirpur",
        )
        assert result["far"] == 2.4
        assert result["ground_coverage_percent"] == 50.0
        assert result["open_space_percent"] == 50.0

    def test_missing_data_insufficient(self):
        result = calculate_density(
            total_floor_area_m2=None,
            plot_area_m2=1000.0,
            footprint_m2=500.0,
            total_occupants=20,
        )
        assert result["far"] is None
        assert "Insufficient" in result["confidence"]
        assert len(result["missing_data"]) > 0

    def test_no_compliance_claim(self):
        result = calculate_density(
            total_floor_area_m2=2400.0,
            plot_area_m2=1000.0,
            footprint_m2=500.0,
            total_occupants=20,
        )
        assert result["status"] == "Estimated"
        # far_compliant should not be set to True (would be a compliance claim)
        assert result.get("far_compliant") is None or result.get("far_compliant") is False