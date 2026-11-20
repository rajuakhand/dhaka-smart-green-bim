"""
Phase 2 tests — Climate data module.

Reference checks against known NASA POWER values for Dhaka and against
published BMD normals.
"""
import math

import pytest

from src.modules.climate import (
    BMD_DHAKA_NORMALS,
    ClimateDataset,
    MONTH_NAMES,
    climate_summary,
    cooling_degree_days,
    fetch_nasa_power,
)


def _synthetic_dataset() -> ClimateDataset:
    """Build a dataset with known values for deterministic tests."""
    monthly = {
        "T2M": {m: 20.0 + m for m in range(1, 13)},          # 21..32
        "T2M_MAX": {m: 30.0 + m for m in range(1, 13)},      # extremes
        "T2M_MIN": {m: 10.0 + m for m in range(1, 13)},
        "RH2M": {m: 70.0 for m in range(1, 13)},
        "WS2M": {m: 2.0 for m in range(1, 13)},
        "ALLSKY_SFC_SW_DWN": {m: 4.0 for m in range(1, 13)},
    }
    return ClimateDataset(
        dataset_id="TEST",
        source_name="Synthetic test data",
        source_url="test://local",
        publisher="test",
        resolution="n/a",
        units={},
        latitude=23.8103,
        longitude=90.4125,
        period="2000-2001",
        monthly=monthly,
    )


class TestClimateSummary:
    def test_mean_uses_t2m_not_extremes(self):
        """CRITICAL: mean temperature must come from T2M, not T2M_MAX/T2M_MIN.

        T2M_MAX/MIN are extremes. Averaging them would inflate the mean.
        Synthetic T2M = 21..32 -> mean = 26.5
        Averaging extremes (31..42 and 11..22) would give 26.5 too here, so we
        use asymmetric data below to prove the difference.
        """
        ds = _synthetic_dataset()
        # Make extremes highly asymmetric so a wrong implementation differs
        ds.monthly["T2M_MAX"] = {m: 45.0 for m in range(1, 13)}
        ds.monthly["T2M_MIN"] = {m: 5.0 for m in range(1, 13)}

        summary = climate_summary(ds)
        assert summary["annual_mean_temp_c"] == 26.5  # from T2M (21..32)
        assert summary["extreme_max_temp_c"] == 45.0
        assert summary["extreme_min_temp_c"] == 5.0

    def test_units_note_present(self):
        summary = climate_summary(_synthetic_dataset())
        assert any("T2M_MAX" in n for n in summary["engineering_notes"])

    def test_missing_ghi_flagged(self):
        ds = _synthetic_dataset()
        del ds.monthly["ALLSKY_SFC_SW_DWN"]
        summary = climate_summary(ds)
        assert summary["annual_mean_ghi_kwh_m2_day"] is None
        assert any("Solar irradiance unavailable" in l for l in summary["limitations"])


class TestCoolingDegreeDays:
    def test_constant_temp_above_base(self):
        ds = _synthetic_dataset()
        ds.monthly["T2M"] = {m: 30.0 for m in range(1, 13)}
        cdd = cooling_degree_days(ds, base_c=26.0)
        # (30-26) * 365.25 days = 1461
        assert abs(cdd["cdd_total"] - 4.0 * 365.25) < 1.0

    def test_constant_temp_below_base(self):
        ds = _synthetic_dataset()
        ds.monthly["T2M"] = {m: 20.0 for m in range(1, 13)}
        cdd = cooling_degree_days(ds, base_c=26.0)
        assert cdd["cdd_total"] == 0.0

    def test_uses_t2m_only(self):
        """CDD must ignore T2M_MAX/T2M_MIN entirely."""
        ds = _synthetic_dataset()
        ds.monthly["T2M"] = {m: 26.0 for m in range(1, 13)}
        cdd_a = cooling_degree_days(ds, base_c=26.0)
        ds.monthly["T2M_MAX"] = {m: 99.0 for m in range(1, 13)}
        ds.monthly["T2M_MIN"] = {m: -99.0 for m in range(1, 13)}
        cdd_b = cooling_degree_days(ds, base_c=26.0)
        assert cdd_a["cdd_total"] == cdd_b["cdd_total"] == 0.0

    def test_unavailable_when_no_temperature(self):
        ds = _synthetic_dataset()
        del ds.monthly["T2M"]
        cdd = cooling_degree_days(ds, 26.0)
        assert cdd["available"] is False
        assert cdd["cdd_total"] is None


class TestGet:
    def test_get_returns_none_when_missing(self):
        """Missing data must be None, never 0."""
        ds = _synthetic_dataset()
        assert ds.get("T2M", 1) == 21.0
        assert ds.get("NONEXISTENT", 1) is None

    def test_to_dict_roundtrip(self):
        ds = _synthetic_dataset()
        blob = ds.to_dict()
        assert blob["dataset_id"] == "TEST"
        # asdict preserves int keys in the monthly mapping
        monthly = blob["monthly"]
        assert monthly["T2M"][1] == 21.0 or monthly["T2M"]["1"] == 21.0


class TestBMDFallback:
    def test_bmd_normals_cover_all_months(self):
        for param in ("T2M_MAX", "T2M_MIN", "RH2M"):
            assert len(BMD_DHAKA_NORMALS[param]) == 12
            assert set(BMD_DHAKA_NORMALS[param].keys()) == set(MONTH_NAMES)

    def test_bmd_dhaka_january_cooler_than_june(self):
        jan_max = BMD_DHAKA_NORMALS["T2M_MAX"]["JAN"]
        jun_max = BMD_DHAKA_NORMALS["T2M_MAX"]["JUN"]
        assert jan_max < jun_max

    def test_bmd_values_are_physically_plausible(self):
        for v in BMD_DHAKA_NORMALS["T2M_MAX"].values():
            assert 20.0 < v < 45.0
        for v in BMD_DHAKA_NORMALS["T2M_MIN"].values():
            assert 5.0 < v < 30.0
        for v in BMD_DHAKA_NORMALS["RH2M"].values():
            assert 40.0 < v < 100.0


class TestDhakaClimateReference:
    """Reference-value tests against published Dhaka climate normals."""

    def test_dhaka_mean_temperature_range(self):
        """Dhaka annual mean is ~26 C. Allow 24-28."""
        ds = fetch_nasa_power(23.8103, 90.4125, 2005, 2024)
        summary = climate_summary(ds)
        assert summary["annual_mean_temp_c"] is not None
        assert 24.0 <= summary["annual_mean_temp_c"] <= 28.0

    def test_dhaka_ghi_in_expected_band(self):
        """Dhaka GHI ~4.0-4.6 kWh/m2/day."""
        ds = fetch_nasa_power(23.8103, 90.4125, 2005, 2024)
        summary = climate_summary(ds)
        assert summary["annual_mean_ghi_kwh_m2_day"] is not None
        assert 3.5 <= summary["annual_mean_ghi_kwh_m2_day"] <= 5.0

    def test_dhaka_extremes_plausible(self):
        """Dhaka extremes: >40 C in April-May, <10 C in winter."""
        ds = fetch_nasa_power(23.8103, 90.4125, 2005, 2024)
        summary = climate_summary(ds)
        assert summary["extreme_max_temp_c"] > 40.0
        assert summary["extreme_min_temp_c"] < 12.0

    def test_dhaka_hottest_month_is_spring(self):
        """Bangladesh's hottest period is April-May (pre-monsoon)."""
        ds = fetch_nasa_power(23.8103, 90.4125, 2005, 2024)
        tmean = ds.monthly["T2M"]
        hottest = max(tmean, key=tmean.get)
        assert hottest in (3, 4, 5)  # March, April or May

    def test_dhaka_cdd_positive(self):
        ds = fetch_nasa_power(23.8103, 90.4125, 2005, 2024)
        cdd = cooling_degree_days(ds, 26.0)
        assert cdd["available"] is True
        assert cdd["cdd_total"] > 0