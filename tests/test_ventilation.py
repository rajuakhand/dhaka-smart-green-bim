"""
Unit tests for Module C — Ventilation Screening.
"""
from src.models.schemas import RoomCreate, RoomType
from src.modules.ventilation import screen_room_ventilation, screen_all_rooms


def make_room(**kwargs) -> RoomCreate:
    defaults = {
        "name": "Test Room",
        "room_type": RoomType.RESIDENTIAL,
        "length_m": 5.0,
        "width_m": 4.0,
        "height_m": 3.0,
        "occupants": 2,
        "window_area_m2": 10.0,  # Set default window area
    }
    defaults.update(kwargs)
    return RoomCreate(**defaults)


class TestVentilationScreening:
    def test_opening_ratio_calculation(self):
        room = make_room(length_m=5, width_m=4, openable_window_area_m2=2.0)
        # Floor area = 20 m², openable = 2 m² → 10%
        result = screen_room_ventilation(room)
        assert result["opening_ratio_percent"] == 10.0

    def test_bnbc_5_percent_pass(self):
        # 5% of 20 m² = 1 m²
        room = make_room(length_m=5, width_m=4, openable_window_area_m2=1.0)
        result = screen_room_ventilation(room)
        assert result["bnbc_min_5_percent"] is True
        assert result["passes_screening"] is True

    def test_bnbc_5_percent_fail(self):
        # 4% of 20 m² = 0.8 m²
        room = make_room(length_m=5, width_m=4, openable_window_area_m2=0.8)
        result = screen_room_ventilation(room)
        assert result["bnbc_min_5_percent"] is False
        assert result["passes_screening"] is False

    def test_zero_openable_area(self):
        room = make_room(length_m=5, width_m=4, openable_window_area_m2=0.0)
        result = screen_room_ventilation(room)
        assert result["opening_ratio_percent"] == 0.0
        assert result["passes_screening"] is False

    def test_cross_ventilation_potential(self):
        # Room with windows, favorable depth
        room = make_room(length_m=5, width_m=4, height_m=3, window_area_m2=10)
        result = screen_room_ventilation(room)
        assert result["cross_ventilation_possible"] in (True, False)  # Boolean
        assert result["depth_to_height_ratio"] > 0

    def test_room_depth_ratio(self):
        # 5m depth / 3m height = 1.67
        room = make_room(length_m=5, width_m=4, height_m=3)
        result = screen_room_ventilation(room)
        assert abs(result["depth_to_height_ratio"] - 1.67) < 0.1

    def test_obstruction_flag(self):
        room = make_room(length_m=5, width_m=4, height_m=3, external_obstruction_height_m=10)
        result = screen_room_ventilation(room)
        assert result["obstruction_flag"] is True

    def test_no_obstruction(self):
        room = make_room(length_m=5, width_m=4, height_m=3, external_obstruction_height_m=0)
        result = screen_room_ventilation(room)
        assert result["obstruction_flag"] is False

    def test_limitations_always_present(self):
        room = make_room(length_m=5, width_m=4)
        result = screen_room_ventilation(room)
        assert len(result["limitations"]) > 0
        assert any("Screening" in l for l in result["limitations"])

    def test_recommendations_for_failing_room(self):
        room = make_room(length_m=5, width_m=4, openable_window_area_m2=0.5)
        result = screen_room_ventilation(room)
        assert len(result["recommendations"]) > 0


class TestScreenAllRooms:
    def test_summary_counts(self):
        rooms = [
            make_room(length_m=5, width_m=4, openable_window_area_m2=2.0),  # 10% pass
            make_room(length_m=5, width_m=4, openable_window_area_m2=0.5),  # 2.5% fail
        ]
        result = screen_all_rooms(rooms)
        assert result["summary"]["rooms_screened"] == 2
        assert result["summary"]["rooms_passing"] == 1
        assert result["summary"]["rooms_below_minimum"] == 1