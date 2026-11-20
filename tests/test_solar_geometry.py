"""
Phase 2 tests — Solar geometry module.

Reference tests verify the astronomical calculations against known values:
  - At equinox, solar declination ~0, so noon zenith at latitude φ ≈ φ.
  - At summer solstice (Jun 21) in Dhaka (23.81 N), the sun passes almost
    directly overhead (declination +23.44 vs latitude 23.81 -> zenith ~0.4 deg).
  - Clear-sky noon GHI in the tropics is ~850-1000 W/m2.
"""
import math

import pandas as pd
import pytest

from src.modules.solar_geometry import (
    DHAKA_LATITUDE,
    DHAKA_LONGITUDE,
    DEFAULT_SHGC,
    compass_label,
    daily_sun_path,
    facade_solar_summary,
    shgc_for_glazing,
    solar_heat_gain,
    solar_position,
    solar_profile_angle,
)

DHAKA_TZ = "Asia/Dhaka"


class TestSolarPosition:
    def test_equinox_noon_zenith_equals_latitude(self):
        """At equinox the sun is over the equator, so noon zenith ≈ latitude."""
        times = pd.date_range("2026-03-20", periods=24, freq="h", tz=DHAKA_TZ)
        pos = solar_position(DHAKA_LATITUDE, DHAKA_LONGITUDE, times)
        noon_zenith = float(pos["apparent_zenith"].iloc[12])
        # Dhaka latitude = 23.81; equinox noon zenith should be ~23.8 (+-1.5)
        assert abs(noon_zenith - DHAKA_LATITUDE) < 1.5

    def test_summer_solstice_near_overhead(self):
        """Jun 21: declination +23.44 vs Dhaka 23.81 -> near-zenith noon."""
        times = pd.date_range("2026-06-21", periods=24, freq="h", tz=DHAKA_TZ)
        pos = solar_position(DHAKA_LATITUDE, DHAKA_LONGITUDE, times)
        noon_zenith = float(pos["apparent_zenith"].iloc[12])
        assert noon_zenith < 5.0  # sun almost directly overhead

    def test_winter_solstice_low_noon_sun(self):
        """Dec 21: noon zenith = latitude + 23.44 ≈ 47.25 deg."""
        times = pd.date_range("2026-12-21", periods=24, freq="h", tz=DHAKA_TZ)
        pos = solar_position(DHAKA_LATITUDE, DHAKA_LONGITUDE, times)
        noon_zenith = float(pos["apparent_zenith"].iloc[12])
        assert abs(noon_zenith - (DHAKA_LATITUDE + 23.44)) < 2.0

    def test_azimuth_at_noon_is_south(self):
        """In Dhaka (northern tropics) the noon sun is due south."""
        times = pd.date_range("2026-03-20", periods=24, freq="h", tz=DHAKA_TZ)
        pos = solar_position(DHAKA_LATITUDE, DHAKA_LONGITUDE, times)
        noon_azimuth = float(pos["azimuth"].iloc[12])
        assert 170.0 <= noon_azimuth <= 190.0

    def test_sun_below_horizon_at_midnight(self):
        times = pd.date_range("2026-03-20", periods=24, freq="h", tz=DHAKA_TZ)
        pos = solar_position(DHAKA_LATITUDE, DHAKA_LONGITUDE, times)
        assert float(pos["apparent_zenith"].iloc[0]) > 90.0


class TestSunPath:
    def test_daylight_hours_near_twelve_at_equinox(self):
        sp = daily_sun_path(DHAKA_LATITUDE, DHAKA_LONGITUDE, pd.Timestamp("2026-03-20"))
        assert 11.0 <= sp["daylight_hours"] <= 13.0

    def test_summer_day_longer_than_winter(self):
        summer = daily_sun_path(DHAKA_LATITUDE, DHAKA_LONGITUDE, pd.Timestamp("2026-06-21"))
        winter = daily_sun_path(DHAKA_LATITUDE, DHAKA_LONGITUDE, pd.Timestamp("2026-12-21"))
        assert summer["daylight_hours"] > winter["daylight_hours"]

    def test_peak_altitude_in_summer_high(self):
        sp = daily_sun_path(DHAKA_LATITUDE, DHAKA_LONGITUDE, pd.Timestamp("2026-06-21"))
        assert sp["peak_altitude_deg"] > 80.0

    def test_samples_are_96_quarter_hours(self):
        sp = daily_sun_path(DHAKA_LATITUDE, DHAKA_LONGITUDE, pd.Timestamp("2026-06-21"))
        assert len(sp["samples"]) == 96

    def test_samples_have_required_fields(self):
        sp = daily_sun_path(DHAKA_LATITUDE, DHAKA_LONGITUDE, pd.Timestamp("2026-06-21"))
        for s in sp["samples"][:3]:
            assert {"time", "altitude_deg", "zenith_deg", "azimuth_deg", "compass"} <= set(s)


class TestFacadeSolar:
    def test_south_facade_highest_in_winter(self):
        """In December the sun is low in the south -> south facade peaks."""
        dec = facade_solar_summary(
            DHAKA_LATITUDE, DHAKA_LONGITUDE, 0.0, pd.Timestamp("2026-12-21")
        )
        # Facade 'Rear' = south when orientation=0
        rear = dec["facades"]["Rear"]["daily_poa_kwh_m2"]
        front = dec["facades"]["Front"]["daily_poa_kwh_m2"]
        assert rear > front

    def test_north_facade_lowest_in_winter(self):
        dec = facade_solar_summary(
            DHAKA_LATITUDE, DHAKA_LONGITUDE, 0.0, pd.Timestamp("2026-12-21")
        )
        front = dec["facades"]["Front"]["daily_poa_kwh_m2"]
        rear = dec["facades"]["Rear"]["daily_poa_kwh_m2"]
        assert front < rear

    def test_east_and_west_higher_than_north_in_summer(self):
        """At summer solstice the sun is near-overhead; E/W get low-angle sun."""
        jun = facade_solar_summary(
            DHAKA_LATITUDE, DHAKA_LONGITUDE, 0.0, pd.Timestamp("2026-06-21")
        )
        east = jun["facades"]["Right"]["daily_poa_kwh_m2"]
        north = jun["facades"]["Front"]["daily_poa_kwh_m2"]
        assert east > north

    def test_all_facade_values_non_negative(self):
        fs = facade_solar_summary(
            DHAKA_LATITUDE, DHAKA_LONGITUDE, 180.0, pd.Timestamp("2026-06-21")
        )
        for name, v in fs["facades"].items():
            assert v["daily_poa_kwh_m2"] >= 0.0
            assert v["peak_poa_w_m2"] >= 0.0

    def test_daily_totals_plausible(self):
        """Clear-sky POA on a facade should be 0-8 kWh/m2/day."""
        fs = facade_solar_summary(
            DHAKA_LATITUDE, DHAKA_LONGITUDE, 0.0, pd.Timestamp("2026-06-21")
        )
        for name, v in fs["facades"].items():
            assert 0.0 <= v["daily_poa_kwh_m2"] <= 8.0

    def test_orientation_rotates_facades(self):
        """Rotating the building by 90 deg swaps which label gets which azimuth."""
        a = facade_solar_summary(DHAKA_LATITUDE, DHAKA_LONGITUDE, 0.0, pd.Timestamp("2026-06-21"))
        b = facade_solar_summary(DHAKA_LATITUDE, DHAKA_LONGITUDE, 90.0, pd.Timestamp("2026-06-21"))
        assert a["facades"]["Front"]["azimuth_deg"] == 0.0
        assert b["facades"]["Front"]["azimuth_deg"] == 90.0


class TestProfileAngle:
    def test_zero_when_sun_behind_facade(self):
        assert solar_profile_angle(45.0, 0.0, 180.0) == 0.0

    def test_zero_when_sun_below_horizon(self):
        assert solar_profile_angle(-10.0, 180.0, 180.0) == 0.0

    def test_equals_altitude_when_sun_faces_facade_squarely(self):
        """cos(0)=1 -> tan(profile)=tan(altitude) -> profile=altitude."""
        assert abs(solar_profile_angle(40.0, 180.0, 180.0) - 40.0) < 1e-6

    def test_monotonic_in_altitude(self):
        low = solar_profile_angle(20.0, 180.0, 180.0)
        high = solar_profile_angle(70.0, 180.0, 180.0)
        assert high > low

    def test_returns_float(self):
        assert isinstance(solar_profile_angle(45.0, 180.0, 180.0), float)


class TestSolarHeatGain:
    def test_basic_formula(self):
        """Q = 4 m2 x 800 W/m2 x 0.82 = 2624 W."""
        r = solar_heat_gain(4.0, 800.0, 0.82)
        assert abs(r["solar_heat_gain_w"] - 2624.0) < 1.0
        assert abs(r["solar_heat_gain_kw"] - 2.624) < 0.001

    def test_zero_area_gives_zero(self):
        assert solar_heat_gain(0.0, 800.0, 0.82)["solar_heat_gain_w"] == 0.0

    def test_zero_irradiance_gives_zero(self):
        assert solar_heat_gain(4.0, 0.0, 0.82)["solar_heat_gain_w"] == 0.0

    def test_shading_factor_scales_linearly(self):
        full = solar_heat_gain(4.0, 800.0, 0.82, shading_factor=1.0)
        half = solar_heat_gain(4.0, 800.0, 0.82, shading_factor=0.5)
        assert abs(half["solar_heat_gain_w"] - full["solar_heat_gain_w"] / 2) < 1.0

    def test_negative_area_raises(self):
        with pytest.raises(ValueError):
            solar_heat_gain(-1.0, 800.0, 0.82)

    def test_invalid_shgc_raises(self):
        with pytest.raises(ValueError):
            solar_heat_gain(4.0, 800.0, 1.5)

    def test_invalid_shading_factor_raises(self):
        with pytest.raises(ValueError):
            solar_heat_gain(4.0, 800.0, 0.82, shading_factor=-0.1)


class TestShgc:
    def test_default_values_in_range(self):
        for v in DEFAULT_SHGC.values():
            assert 0.0 <= v <= 1.0

    def test_custom_shgc_overrides(self):
        assert shgc_for_glazing("Clear", 0.25) == 0.25

    def test_custom_shgc_validated(self):
        with pytest.raises(ValueError):
            shgc_for_glazing("Clear", 1.5)

    def test_unknown_type_falls_back(self):
        assert shgc_for_glazing("Unknown Type") == DEFAULT_SHGC["Other"]

    def test_low_e_lower_than_clear(self):
        assert shgc_for_glazing("Double low-E") < shgc_for_glazing("Clear")


class TestCompassLabel:
    def test_cardinal_directions(self):
        assert compass_label(0.0) == "North"
        assert compass_label(90.0) == "East"
        assert compass_label(180.0) == "South"
        assert compass_label(270.0) == "West"

    def test_wraps_360_to_north(self):
        assert compass_label(360.0) == "North"
        assert compass_label(359.0) == "North"

    def test_intercardinal(self):
        assert compass_label(45.0) == "North-East"
        assert compass_label(225.0) == "South-West"