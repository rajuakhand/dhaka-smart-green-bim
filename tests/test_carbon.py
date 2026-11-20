"""
Unit tests for Module F — Carbon Calculator.
"""
import pytest
from src.modules.carbon import calculate_carbon


class TestCalculateCarbon:
    def test_basic_calculation(self):
        # 125,000 kWh × 0.62 kg/kWh = 77,500 kg CO2e
        result = calculate_carbon(125000.0, "DoE-GEF")
        assert abs(result["operational_emissions_kg_co2e_per_year"] - 77500.0) < 10

    def test_tonnes_conversion(self):
        result = calculate_carbon(125000.0, "DoE-GEF")
        assert abs(result["operational_emissions_t_co2e_per_year"] - 77.5) < 0.01

    def test_ember_factor(self):
        # Ember 0.696 kg/kWh
        result = calculate_carbon(100000.0, "Ember-OWID")
        assert abs(result["emission_factor_kg_co2_per_kwh"] - 0.696) < 0.001
        assert abs(result["operational_emissions_kg_co2e_per_year"] - 69600.0) < 10

    def test_zero_electricity(self):
        result = calculate_carbon(0.0, "DoE-GEF")
        assert result["operational_emissions_kg_co2e_per_year"] == 0.0

    def test_negative_electricity_raises(self):
        with pytest.raises(ValueError):
            calculate_carbon(-1000.0, "DoE-GEF")

    def test_embodied_carbon_is_null(self):
        result = calculate_carbon(125000.0, "DoE-GEF")
        assert result["embodied_carbon"] is None

    def test_source_metadata(self):
        result = calculate_carbon(125000.0, "DoE-GEF")
        assert result["emission_factor_source"] == "DoE-GEF"
        assert result["emission_factor_year"] == 2022
        assert "location-based" in result["emission_scope"]

    def test_limitations_always_present(self):
        result = calculate_carbon(125000.0, "DoE-GEF")
        assert len(result["limitations"]) > 0
        assert any("embodied" in l.lower() for l in result["limitations"])

    def test_confidence_high_for_verified_source(self):
        result = calculate_carbon(125000.0, "DoE-GEF")
        assert "High" in result["confidence"]

    def test_confidence_low_for_unverified(self):
        result = calculate_carbon(125000.0, "User-supplied")
        assert "Low" in result["confidence"]