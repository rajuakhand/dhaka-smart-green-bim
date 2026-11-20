"""
Unit tests for Module D — Daylight Screening.
"""
from src.models.schemas import RoomCreate, RoomType, GlazingType, ShadingType
from src.modules.daylight import screen_room_daylight, screen_all_rooms_daylight


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


class TestDaylightScreening:
    def test_glazing_ratio_calculation(self):
        # floor area = 20 m², window = 4 m² → 20%
        room = make_room(length_m=5, width_m=4, window_area_m2=4.0)
        result = screen_room_daylight(room)
        assert abs(result["wwr_percent"] - 4.0/54.0*100) < 0.5  # wwr vs wall

    def test_bnbc_10_percent_pass(self):
        # 10% of 20 m² = 2 m²
        room = make_room(length_m=5, width_m=4, window_area_m2=2.0)
        result = screen_room_daylight(room)
        assert result["bnbc_min_10_percent"] is True

    def test_bnbc_10_percent_fail(self):
        # 8% of 20 m² = 1.6 m²
        room = make_room(length_m=5, width_m=4, window_area_m2=1.6)
        result = screen_room_daylight(room)
        assert result["bnbc_min_10_percent"] is False

    def test_glazing_vt_by_type(self):
        room = make_room(window_area_m2=4.0, glazing_type=GlazingType.DOUBLE_LOW_E)
        result = screen_room_daylight(room)
        assert result["glazing_vt"] == 0.75

    def test_obstruction_reduces_effective(self):
        room = make_room(window_area_m2=4.0, external_obstruction_height_m=5.0)
        result = screen_room_daylight(room)
        assert result["effective_glazing_with_obstruction_percent"] < 20.0

    def test_overhang_shading(self):
        room = make_room(window_area_m2=4.0, shading_type=ShadingType.OVERHANG)
        result = screen_room_daylight(room)
        assert result["overhang_shading"] is True

    def test_daylight_potential_labels(self):
        # 20% glazing → Adequate
        room = make_room(length_m=5, width_m=4, window_area_m2=4.0)
        result = screen_room_daylight(room)
        assert result["daylight_potential"] == "Adequate"

        # 6% glazing → Marginal
        room = make_room(length_m=5, width_m=4, window_area_m2=1.2)
        result = screen_room_daylight(room)
        assert result["daylight_potential"] in ("Marginal", "Insufficient")

    def test_no_simulation_limitations(self):
        room = make_room(window_area_m2=4.0)
        result = screen_room_daylight(room)
        assert any("sDA" in l or "simulation" in l for l in result["limitations"])

    def test_wwr_calculation_accuracy(self):
        # 5m × 4m, 3m height → wall = 2*(5+4)*3 = 54 m²
        # window 5.4 m² → 10% WWR
        room = make_room(length_m=5, width_m=4, height_m=3, window_area_m2=5.4)
        result = screen_room_daylight(room)
        assert abs(result["wwr_percent"] - 10.0) < 0.5