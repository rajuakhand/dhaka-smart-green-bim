"""
Unit tests for Module E — Preliminary Energy Estimator.
"""
from src.models.schemas import RoomCreate, RoomType
from src.modules.energy import estimate_room_energy, estimate_building_energy


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


class TestEstimateRoomEnergy:
    def test_cooling_energy_calculation(self):
        # Floor area = 20 m², AC capacity = 60 W/m², COP = 3.1, hours = 1800
        # Cooling = (60 × 20 × 1800) / 3.1 / 1000 = 697.7 kWh
        room = make_room(length_m=5, width_m=4)
        result = estimate_room_energy(room, ac_cop=3.1, cooling_hours=1800)
        expected = (60 * 20 * 1800) / (3.1 * 1000)
        assert abs(result["cooling_kwh"] - expected) < 5

    def test_lighting_energy_calculation(self):
        # Floor = 20 m², density = 7 W/m², hours = 2500
        # Lighting = 7 × 20 × 2500 / 1000 = 350 kWh
        room = make_room(length_m=5, width_m=4)
        result = estimate_room_energy(room, lighting_hours=2500)
        expected = 7.0 * 20.0 * 2500.0 / 1000.0
        assert abs(result["lighting_kwh"] - expected) < 5

    def test_equipment_energy_calculation(self):
        # Floor = 20 m², density = 5 W/m², hours = 2500
        # Equipment = 5 × 20 × 2500 / 1000 = 250 kWh
        room = make_room(length_m=5, width_m=4)
        result = estimate_room_energy(room, equipment_hours=2500)
        expected = 5.0 * 20.0 * 2500.0 / 1000.0
        assert abs(result["equipment_kwh"] - expected) < 5

    def test_total_is_sum_of_components(self):
        room = make_room(length_m=5, width_m=4)
        result = estimate_room_energy(room)
        total = result["cooling_kwh"] + result["lighting_kwh"] + result["equipment_kwh"]
        assert abs(result["total_kwh"] - total) < 0.1


class TestEstimateBuildingEnergy:
    def test_epi_calculation(self):
        rooms = [
            make_room(name="Living", length_m=5, width_m=4, occupants=2),
            make_room(name="Bedroom", length_m=3, width_m=3, occupants=1),
            make_room(name="Kitchen", length_m=3, width_m=3, occupants=1),
        ]
        result = estimate_building_energy(rooms)
        assert result["total_floor_area_m2"] == 20.0 + 9.0 + 9.0
        assert result["energy_performance_index_kwh_m2"] > 0

    def test_assumptions_recorded(self):
        rooms = [make_room()]
        result = estimate_building_energy(rooms, ac_cop=3.5)
        assert result["assumptions"]["ac_cop"] == 3.5

    def test_limitations_present(self):
        rooms = [make_room()]
        result = estimate_building_energy(rooms)
        assert len(result["limitations"]) > 0
        assert any("simulation" in l.lower() for l in result["limitations"])

    def test_status_is_estimated_not_verified(self):
        rooms = [make_room()]
        result = estimate_building_energy(rooms)
        assert result["status"] == "Estimated"