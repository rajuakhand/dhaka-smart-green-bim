"""
Unit tests for Module B — Room Analyzer.
"""
import pytest
from src.models.schemas import RoomCreate, RoomType
from src.modules.room_analyzer import analyze_room, analyze_rooms, BNBC_OCCUPANCY_MIN_AREA_M2


def make_room(**kwargs) -> RoomCreate:
    defaults = {
        "name": "Living Room",
        "room_type": RoomType.RESIDENTIAL,
        "length_m": 5.0,
        "width_m": 4.0,
        "height_m": 3.0,
        "occupants": 4,
    }
    defaults.update(kwargs)
    return RoomCreate(**defaults)


class TestAnalyzeRoom:
    def test_floor_area(self):
        room = make_room(length_m=5.0, width_m=4.0)
        result = analyze_room(room)
        assert result["floor_area_m2"] == 20.0

    def test_volume(self):
        room = make_room(length_m=5.0, width_m=4.0, height_m=3.0)
        result = analyze_room(room)
        assert result["volume_m3"] == 60.0

    def test_area_per_person(self):
        room = make_room(length_m=10.0, width_m=5.0, occupants=10)  # 50 m² / 10 = 5 m²/pers
        result = analyze_room(room)
        assert result["area_per_person_m2"] == 5.0

    def test_occupancy_passes(self):
        room = make_room(length_m=10.0, width_m=10.0, occupants=5)  # 100 m² / 5 = 20 m²/pers > 9.3
        result = analyze_room(room)
        assert result["occupancy_passes_screening"] is True

    def test_occupancy_fails(self):
        room = make_room(length_m=3.0, width_m=3.0, occupants=5)  # 9 m² / 5 = 1.8 m²/pers < 9.3
        result = analyze_room(room)
        assert result["occupancy_passes_screening"] is False

    def test_wwr_calculation(self):
        room = make_room(length_m=5.0, width_m=4.0, height_m=3.0, window_area_m2=5.0)
        # wall area = 2*(5+4)*3 = 54 m²
        # wwr = 5/54*100 = 9.26%
        result = analyze_room(room)
        assert 9.0 <= result["window_to_wall_ratio_percent"] <= 9.5

    def test_zero_occupants_edge(self):
        # This should fail validation (occupants >= 1)
        with pytest.raises(Exception):
            make_room(occupants=0)


class TestAnalyzeRooms:
    def test_multiple_rooms(self):
        rooms = [
            make_room(name="Living", length_m=5, width_m=4, occupants=2),
            make_room(name="Bedroom", room_type=RoomType.RESIDENTIAL, length_m=3, width_m=3, occupants=2),
            make_room(name="Kitchen", room_type=RoomType.RESIDENTIAL, length_m=3, width_m=3, occupants=1),
        ]
        result = analyze_rooms(rooms)
        assert result["summary"]["total_rooms"] == 3
        assert result["summary"]["total_floor_area_m2"] == 20.0 + 9.0 + 9.0

    def test_confidence_high_when_all_pass(self):
        rooms = [
            make_room(length_m=10, width_m=10, occupants=1),
        ]
        result = analyze_rooms(rooms)
        assert "High" in result["overall_confidence"]

    def test_confidence_low_when_many_fail(self):
        rooms = [
            make_room(length_m=1, width_m=1, occupants=5),
            make_room(length_m=1, width_m=1, occupants=5),
            make_room(length_m=1, width_m=1, occupants=5),
        ]
        result = analyze_rooms(rooms)
        assert "Low" in result["overall_confidence"]