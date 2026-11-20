"""
Unit tests for Module I — Design Optimization Comparison.
"""
from src.models.schemas import RoomCreate, RoomType
from src.modules.optimization import compare_energy_cases


def make_room(**kwargs) -> RoomCreate:
    defaults = {
        "name": "Test Room",
        "room_type": RoomType.RESIDENTIAL,
        "length_m": 5.0,
        "width_m": 4.0,
        "height_m": 3.0,
        "occupants": 2,
    }
    defaults.update(kwargs)
    return RoomCreate(**defaults)


class TestCompareEnergyCases:
    def test_baseline_value_reported(self):
        rooms = [make_room()]
        result = compare_energy_cases(
            rooms=rooms,
            baseline_assumptions={
                "ac_cop": 3.1,
                "cooling_hours": 1800,
                "lighting_hours": 2500,
                "equipment_hours": 2500,
            },
            alternatives=[],
        )
        assert result["baseline_module"] == "E"
        assert result["baseline_metric_value"] > 0

    def test_alternative_with_higher_cop(self):
        rooms = [make_room()]
        result = compare_energy_cases(
            rooms=rooms,
            baseline_assumptions={
                "ac_cop": 3.1,
                "cooling_hours": 1800,
                "lighting_hours": 2500,
                "equipment_hours": 2500,
            },
            alternatives=[
                {
                    "name": "Higher COP AC",
                    "changes": {"ac_cop": 4.0},
                },
            ],
        )
        assert len(result["alternatives"]) == 1
        alt = result["alternatives"][0]
        assert alt["alternative_epi"] < alt["baseline_epi"]  # Higher COP = less energy
        assert alt["percent_difference"] < 0  # Negative = improvement

    def test_alternative_with_lower_cop(self):
        rooms = [make_room()]
        result = compare_energy_cases(
            rooms=rooms,
            baseline_assumptions={
                "ac_cop": 3.1,
                "cooling_hours": 1800,
                "lighting_hours": 2500,
                "equipment_hours": 2500,
            },
            alternatives=[
                {
                    "name": "Lower COP AC",
                    "changes": {"ac_cop": 2.5},
                },
            ],
        )
        alt = result["alternatives"][0]
        assert alt["alternative_epi"] > alt["baseline_epi"]  # Lower COP = more energy
        assert alt["percent_difference"] > 0

    def test_multiple_alternatives(self):
        rooms = [make_room()]
        result = compare_energy_cases(
            rooms=rooms,
            baseline_assumptions={
                "ac_cop": 3.1,
                "cooling_hours": 1800,
                "lighting_hours": 2500,
                "equipment_hours": 2500,
            },
            alternatives=[
                {"name": "Alt 1", "changes": {"ac_cop": 3.5}},
                {"name": "Alt 2", "changes": {"ac_cop": 4.0}},
            ],
        )
        assert len(result["alternatives"]) == 2

    def test_limitations_always_present(self):
        rooms = [make_room()]
        result = compare_energy_cases(
            rooms=rooms,
            baseline_assumptions={
                "ac_cop": 3.1,
                "cooling_hours": 1800,
                "lighting_hours": 2500,
                "equipment_hours": 2500,
            },
            alternatives=[],
        )
        assert len(result["limitations"]) > 0

    def test_same_baseline_assumptions_used(self):
        rooms = [make_room()]
        result = compare_energy_cases(
            rooms=rooms,
            baseline_assumptions={
                "ac_cop": 3.1,
                "cooling_hours": 1800,
                "lighting_hours": 2500,
                "equipment_hours": 2500,
            },
            alternatives=[],
        )
        assert result["method"] == "Preliminary energy estimator (same assumptions, changed inputs)"