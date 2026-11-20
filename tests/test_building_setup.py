"""
Unit tests for Module A — Building Setup.
"""
import pytest
from src.models.schemas import BuildingCreate, BuildingType, StructuralSystem
from src.modules.building_setup import validate_building, building_summary
from src.core.exceptions import GeometryError


def make_building(**kwargs) -> BuildingCreate:
    defaults = {
        "name": "Test Project",
        "building_type": BuildingType.RESIDENTIAL,
        "num_floors": 6,
        "floor_to_floor_height_m": 3.0,
        "plot_area_m2": 500.0,
        "building_footprint_m2": 200.0,
    }
    defaults.update(kwargs)
    return BuildingCreate(**defaults)


class TestValidateBuilding:
    def test_valid_building(self):
        b = make_building()
        result = validate_building(b)
        assert result["validated"] is True
        assert result["errors"] == []
        assert result["normalized"]["building_type"] == "Residential"

    def test_footprint_exceeds_plot_raises(self):
        b = make_building(building_footprint_m2=600.0, plot_area_m2=500.0)
        with pytest.raises(GeometryError, match="exceeds plot area"):
            validate_building(b)

    def test_high_coverage_warning(self):
        b = make_building(building_footprint_m2=480.0, plot_area_m2=500.0)
        result = validate_building(b)
        assert any("footprint" in w.lower() for w in result["warnings"])

    def test_missing_plot_area(self):
        b = make_building(plot_area_m2=None)
        result = validate_building(b)
        assert result["validated"] is True  # Not an error, just missing
        assert result["normalized"]["plot_area_m2"] is None

    def test_building_summary_valid(self):
        b = make_building()
        summary = building_summary(b)
        assert summary["status"] == "Estimated"
        assert summary["confidence"] == "Medium confidence"


class TestGeometryValidation:
    def test_minimum_floors(self):
        with pytest.raises(Exception):
            make_building(num_floors=0)

    def test_maximum_floors(self):
        with pytest.raises(Exception):
            make_building(num_floors=51)

    def test_height_bounds(self):
        with pytest.raises(Exception):
            make_building(floor_to_floor_height_m=1.5)

    def test_negative_footprint(self):
        with pytest.raises(Exception):
            make_building(building_footprint_m2=-100)