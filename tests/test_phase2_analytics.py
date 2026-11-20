"""
Phase 2 tests — Daylight factor, shading, sensitivity, parametric, materials.

Every calculation has a hand-checkable reference value.
"""
import math

import pandas as pd
import pytest

from src.core.exceptions import ValidationFailure
from src.modules.daylight_factor import (
    DEFAULT_MAINTENANCE_FACTOR,
    GLAZING_TRANSMITTANCE,
    average_daylight_factor,
    df_to_lux_estimate,
    glazing_transmittance,
    internal_surface_area,
    visible_sky_angle,
)
from src.modules.materials import (
    GLAZING_ASSEMBLIES,
    ROOF_CONCRETE,
    ROOF_CONCRETE_INSULATED,
    WALL_150_BRICK_PLASTER,
    WALL_BRICK_INSULATED,
    envelope_summary,
    get_assembly,
    list_assemblies,
    u_value_from_layers,
)
from src.modules.parametric import grid_search, random_search
from src.modules.sensitivity import one_at_a_time_sensitivity
from src.modules.shading import (
    facade_shading_analysis,
    fin_shaded_fraction,
    overhang_shaded_fraction,
    required_overhang_depth,
    shadow_length,
)


# --------------------------------------------------------------------------
# Daylight factor
# --------------------------------------------------------------------------

class TestInternalSurfaceArea:
    def test_reference_value(self):
        """5x4x3 room: 20 (floor) + 20 (ceiling) + 54 (walls) = 94 m2."""
        assert internal_surface_area(5, 4, 3) == pytest.approx(94.0)

    def test_scales_with_size(self):
        assert internal_surface_area(10, 10, 3) > internal_surface_area(5, 5, 3)

    def test_zero_dimension_raises(self):
        with pytest.raises(ValidationFailure):
            internal_surface_area(0, 4, 3)


class TestVisibleSkyAngle:
    def test_reference_value(self):
        """2*atan(1.5/(2*2.5)) = 2*atan(0.3) = 0.5829 rad."""
        theta = visible_sky_angle(2.0, 1.5, 5.0, 4.0)
        assert theta == pytest.approx(0.5829, abs=1e-3)

    def test_zero_height_gives_zero(self):
        assert visible_sky_angle(2.0, 0.0, 5.0, 4.0) == 0.0

    def test_taller_window_larger_angle(self):
        small = visible_sky_angle(2.0, 0.5, 5.0, 4.0)
        large = visible_sky_angle(2.0, 2.5, 5.0, 4.0)
        assert large > small

    def test_deeper_room_smaller_angle(self):
        near = visible_sky_angle(2.0, 1.5, 3.0, 3.0)
        far = visible_sky_angle(2.0, 1.5, 10.0, 10.0)
        assert near > far


class TestAverageDaylightFactor:
    def test_reference_value(self):
        """Hand-checkable: M=0.8, T=0.85, W=3, theta=0.5829, A=94, R=0.5.

        DF = (0.8*0.85*3*0.5829) / (94*(1-0.25)) = 1.1891 / 70.5 = 0.016867
           = 1.6867 %
        """
        r = average_daylight_factor(
            window_area_m2=3.0, window_width_m=2.0, window_height_m=1.5,
            room_length_m=5.0, room_width_m=4.0, room_height_m=3.0,
            glazing_type="Clear",
        )
        assert r["daylight_factor_percent"] == pytest.approx(1.687, abs=0.01)

    def test_more_window_increases_df(self):
        base = average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3)
        bigger = average_daylight_factor(6.0, 3.0, 2.0, 5, 4, 3)
        assert bigger["daylight_factor_percent"] > base["daylight_factor_percent"]

    def test_better_glazing_increases_df(self):
        clear = average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3, glazing_type="Clear")
        lowe = average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3, glazing_type="Double low-E")
        assert clear["daylight_factor_percent"] > lowe["daylight_factor_percent"]

    def test_obstruction_reduces_df(self):
        clear = average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3, obstruction_height_m=0)
        blocked = average_daylight_factor(
            3.0, 2.0, 1.5, 5, 4, 3, obstruction_height_m=9.0, obstruction_distance_m=6.0
        )
        assert blocked["daylight_factor_percent"] < clear["daylight_factor_percent"]
        assert blocked["confidence"] == "Low confidence"

    def test_negative_window_raises(self):
        with pytest.raises(ValidationFailure):
            average_daylight_factor(-1.0, 2.0, 1.5, 5, 4, 3)

    def test_zero_area_raises(self):
        with pytest.raises(ValidationFailure):
            average_daylight_factor(0.0, 2.0, 1.5, 5, 4, 3)

    def test_invalid_reflectance_raises(self):
        with pytest.raises(ValidationFailure):
            average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3, reflectance=1.5)

    def test_invalid_maintenance_factor_raises(self):
        with pytest.raises(ValidationFailure):
            average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3, maintenance_factor=1.5)

    def test_df_is_non_negative(self):
        r = average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3)
        assert r["daylight_factor_percent"] >= 0.0

    def test_limitations_always_present(self):
        r = average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3)
        assert len(r["limitations"]) > 0
        assert any("Radiance" in l for l in r["limitations"])

    def test_method_recorded(self):
        r = average_daylight_factor(3.0, 2.0, 1.5, 5, 4, 3)
        assert "CIBSE" in r["method"]


class TestGlazingTransmittance:
    def test_defaults_in_range(self):
        for v in GLAZING_TRANSMITTANCE.values():
            assert 0.0 < v <= 1.0

    def test_custom_overrides(self):
        assert glazing_transmittance("Clear", 0.5) == 0.5

    def test_custom_validated(self):
        with pytest.raises(ValidationFailure):
            glazing_transmittance("Clear", 0.0)
        with pytest.raises(ValidationFailure):
            glazing_transmittance("Clear", 1.5)


class TestDfToLux:
    def test_reference_value(self):
        """DF 2% with 10,000 lux sky -> 200 lux interior."""
        r = df_to_lux_estimate(2.0, 10000.0)
        assert r["indicative_interior_illuminance_lux"] == pytest.approx(200.0)

    def test_zero_df_gives_zero_lux(self):
        assert df_to_lux_estimate(0.0)["indicative_interior_illuminance_lux"] == 0.0

    def test_status_is_estimated(self):
        assert df_to_lux_estimate(2.0)["status"] == "Estimated"

    def test_negative_df_raises(self):
        with pytest.raises(ValidationFailure):
            df_to_lux_estimate(-1.0)


# --------------------------------------------------------------------------
# Shading
# --------------------------------------------------------------------------

class TestShadowLength:
    def test_reference_45_degrees(self):
        """L = 10 / tan(45) = 10 m."""
        assert shadow_length(10.0, 45.0) == pytest.approx(10.0, abs=0.01)

    def test_reference_30_degrees(self):
        """L = 10 / tan(30) = 17.32 m."""
        assert shadow_length(10.0, 30.0) == pytest.approx(17.32, abs=0.05)

    def test_sun_at_horizon_gives_zero(self):
        assert shadow_length(10.0, 0.0) == 0.0
        assert shadow_length(10.0, -5.0) == 0.0

    def test_negative_height_raises(self):
        with pytest.raises(ValidationFailure):
            shadow_length(-1.0, 45.0)

    def test_lower_sun_longer_shadow(self):
        assert shadow_length(10.0, 20.0) > shadow_length(10.0, 60.0)


class TestRequiredOverhang:
    def test_reference_60_degrees(self):
        """d = 1.5 / tan(60) = 0.866 m."""
        assert required_overhang_depth(1.5, 60.0) == pytest.approx(0.866, abs=0.005)

    def test_reference_45_degrees(self):
        assert required_overhang_depth(1.5, 45.0) == pytest.approx(1.5, abs=0.01)

    def test_zero_profile_gives_zero(self):
        assert required_overhang_depth(1.5, 0.0) == 0.0

    def test_non_positive_window_raises(self):
        with pytest.raises(ValidationFailure):
            required_overhang_depth(0.0, 60.0)


class TestOverhangShadedFraction:
    def test_full_shading(self):
        """The exact required depth for 1.5 m at 60 deg fully shades the window."""
        depth = required_overhang_depth(1.5, 60.0)
        r = overhang_shaded_fraction(1.5, depth + 0.01, 60.0)
        assert r["fully_shaded"] is True
        assert r["shaded_percent"] == pytest.approx(100.0, abs=0.5)

    def test_partial_shading(self):
        r = overhang_shaded_fraction(1.5, 0.4, 60.0)
        assert 0.0 < r["shaded_fraction"] < 1.0

    def test_zero_overhang_no_shade(self):
        r = overhang_shaded_fraction(1.5, 0.0, 60.0)
        assert r["shaded_percent"] == 0.0

    def test_fraction_never_exceeds_one(self):
        r = overhang_shaded_fraction(1.0, 10.0, 80.0)
        assert r["shaded_fraction"] <= 1.0

    def test_invalid_input_raises(self):
        with pytest.raises(ValidationFailure):
            overhang_shaded_fraction(-1.0, 0.5, 60.0)
        with pytest.raises(ValidationFailure):
            overhang_shaded_fraction(1.5, -0.5, 60.0)


class TestFinShadedFraction:
    def test_partial_shading(self):
        r = fin_shaded_fraction(2.0, 0.5, 45.0)
        assert 0.0 < r["shaded_fraction"] < 1.0

    def test_zero_fin_no_shade(self):
        assert fin_shaded_fraction(2.0, 0.0, 45.0)["shaded_percent"] == 0.0

    def test_fraction_capped(self):
        r = fin_shaded_fraction(1.0, 5.0, 80.0)
        assert r["shaded_fraction"] <= 1.0


class TestFacadeShadingAnalysis:
    def test_returns_48_samples(self):
        r = facade_shading_analysis(facade_azimuth_deg=180.0, date=pd.Timestamp("2026-06-21"))
        assert len(r["samples"]) == 48

    def test_night_samples_not_sunlit(self):
        r = facade_shading_analysis(facade_azimuth_deg=180.0, date=pd.Timestamp("2026-06-21"))
        first = r["samples"][0]
        assert first["sun_on_facade"] is False

    def test_peak_profile_positive_in_day(self):
        r = facade_shading_analysis(facade_azimuth_deg=180.0, date=pd.Timestamp("2026-06-21"))
        assert r["peak_profile_angle_deg"] > 0.0

    def test_overhang_reduces_sunlight(self):
        bare = facade_shading_analysis(
            facade_azimuth_deg=180.0, overhang_depth_m=0.0, date=pd.Timestamp("2026-03-21")
        )
        shaded = facade_shading_analysis(
            facade_azimuth_deg=180.0, overhang_depth_m=1.0, date=pd.Timestamp("2026-03-21")
        )
        shaded_pct_bare = sum(s["overhang_shaded_percent"] for s in bare["samples"])
        shaded_pct_shaded = sum(s["overhang_shaded_percent"] for s in shaded["samples"])
        assert shaded_pct_shaded > shaded_pct_bare

    def test_obstruction_reported(self):
        r = facade_shading_analysis(
            facade_azimuth_deg=180.0, obstruction_height_m=12.0,
            obstruction_distance_m=9.0, date=pd.Timestamp("2026-03-21")
        )
        assert r["obstruction"] is not None
        assert r["obstruction"]["vertical_blocking_angle_deg"] == pytest.approx(53.13, abs=0.1)
        assert r["confidence"] == "Low confidence"

    def test_limitations_present(self):
        r = facade_shading_analysis()
        assert len(r["limitations"]) > 0
        assert any("box-model" in l.lower() for l in r["limitations"])

    def test_negative_shading_raises(self):
        with pytest.raises(ValidationFailure):
            facade_shading_analysis(overhang_depth_m=-1.0)


# --------------------------------------------------------------------------
# Sensitivity
# --------------------------------------------------------------------------

def _linear_metric(d: dict) -> float:
    """metric = 2*a + 3*b; analytically known elasticities."""
    return 2.0 * d["a"] + 3.0 * d["b"]


class TestSensitivity:
    def test_ranking_by_elasticity(self):
        r = one_at_a_time_sensitivity(
            {"a": 10.0, "b": 10.0}, _linear_metric, delta=0.10
        )
        assert r["ranking_by_influence"] == ["b", "a"]

    def test_baseline_metric_recorded(self):
        r = one_at_a_time_sensitivity({"a": 10.0, "b": 10.0}, _linear_metric)
        assert r["baseline_metric"] == pytest.approx(50.0)

    def test_elasticity_sign_for_positive_term(self):
        r = one_at_a_time_sensitivity({"a": 10.0, "b": 10.0}, _linear_metric, delta=0.10)
        row = [x for x in r["results"] if x["parameter"] == "a"][0]
        assert row["elasticity"] > 0

    def test_elasticity_sign_for_negative_term(self):
        """metric = 50 - 3*b (baseline 20); raising b lowers the metric."""
        r = one_at_a_time_sensitivity(
            {"b": 10.0}, lambda d: 50.0 - 3.0 * d["b"], delta=0.10
        )
        row = [x for x in r["results"] if x["parameter"] == "b"][0]
        assert row["elasticity"] < 0

    def test_zero_baseline_raises(self):
        """A zero baseline makes elasticity undefined -> must raise, not fake."""
        with pytest.raises(ValidationFailure):
            one_at_a_time_sensitivity({"a": 10.0, "b": 10.0}, lambda d: d["a"] - d["b"])

    def test_invalid_delta_raises(self):
        with pytest.raises(ValidationFailure):
            one_at_a_time_sensitivity({"a": 10.0}, _linear_metric, delta=0.0)
        with pytest.raises(ValidationFailure):
            one_at_a_time_sensitivity({"a": 10.0}, _linear_metric, delta=2.0)

    def test_non_callable_metric_raises(self):
        with pytest.raises(ValidationFailure):
            one_at_a_time_sensitivity({"a": 1.0}, "not callable")

    def test_limitations_present(self):
        r = one_at_a_time_sensitivity({"a": 10.0, "b": 10.0}, _linear_metric)
        assert any("interaction" in l.lower() for l in r["limitations"])

    def test_deterministic_repeatability(self):
        a = one_at_a_time_sensitivity({"a": 10.0, "b": 10.0}, _linear_metric)
        b = one_at_a_time_sensitivity({"a": 10.0, "b": 10.0}, _linear_metric)
        assert a["ranking_by_influence"] == b["ranking_by_influence"]
        assert a["baseline_metric"] == b["baseline_metric"]


# --------------------------------------------------------------------------
# Parametric optimization
# --------------------------------------------------------------------------

class TestGridSearch:
    def test_finds_known_minimum(self):
        """Objective = (x-3)^2 has minimum 0 at x=3, which is in the space."""
        space = {"x": [0, 1, 2, 3, 4, 5]}
        r = grid_search(space, lambda d: (d["x"] - 3.0) ** 2)
        assert r["best"]["design"]["x"] == 3
        assert r["best"]["objective"] == pytest.approx(0.0)

    def test_finds_known_maximum(self):
        space = {"x": [0, 1, 2, 3, 4, 5]}
        r = grid_search(space, lambda d: d["x"], maximise=True)
        assert r["best"]["design"]["x"] == 5

    def test_evaluates_full_grid(self):
        space = {"a": [1, 2], "b": [3, 4, 5]}
        r = grid_search(space, lambda d: d["a"] + d["b"])
        assert r["evaluated"] == 6
        assert r["design_space_size"] == 6

    def test_constraints_reject(self):
        space = {"a": [1, 2, 3, 4]}
        r = grid_search(
            space, lambda d: d["a"], constraints={"positive": lambda d: d["a"] > 0}
        )
        assert r["evaluated"] == 4
        assert r["rejected_by_constraints"] == 0

        r2 = grid_search(
            space, lambda d: d["a"], constraints={"big": lambda d: d["a"] > 10}
        )
        assert r2["best"] is None
        assert r2["status"] == "Insufficient data"

    def test_ranking_sorted_ascending_by_default(self):
        space = {"x": [5, 1, 3]}
        r = grid_search(space, lambda d: d["x"])
        objectives = [row["objective"] for row in r["ranking"]]
        assert objectives == sorted(objectives)

    def test_ranking_sorted_descending_when_maximise(self):
        space = {"x": [5, 1, 3]}
        r = grid_search(space, lambda d: d["x"], maximise=True)
        objectives = [row["objective"] for row in r["ranking"]]
        assert objectives == sorted(objectives, reverse=True)

    def test_empty_space_raises(self):
        with pytest.raises(ValidationFailure):
            grid_search({}, lambda d: 0.0)

    def test_empty_candidate_list_raises(self):
        with pytest.raises(ValidationFailure):
            grid_search({"a": []}, lambda d: 0.0)

    def test_limitations_present(self):
        r = grid_search({"x": [1, 2]}, lambda d: d["x"])
        assert len(r["limitations"]) > 0


class TestRandomSearch:
    def test_deterministic_for_seed(self):
        space = {"x": [1, 2, 3, 4, 5], "y": [10, 20, 30]}
        a = random_search(space, lambda d: d["x"] + d["y"], n_samples=20, seed=7)
        b = random_search(space, lambda d: d["x"] + d["y"], n_samples=20, seed=7)
        assert a["best"] == b["best"]
        assert a["ranking"] == b["ranking"]

    def test_different_seed_may_differ(self):
        space = {"x": list(range(100))}
        a = random_search(space, lambda d: d["x"], n_samples=5, seed=1)
        b = random_search(space, lambda d: d["x"], n_samples=5, seed=999)
        # Very likely different, but assert only that both are valid
        assert 0 <= a["best"]["design"]["x"] < 100
        assert 0 <= b["best"]["design"]["x"] < 100

    def test_invalid_n_samples_raises(self):
        with pytest.raises(ValidationFailure):
            random_search({"x": [1]}, lambda d: 0.0, n_samples=0)

    def test_limitations_present(self):
        r = random_search({"x": [1, 2]}, lambda d: d["x"], n_samples=5)
        assert any("Stochastic" in l for l in r["limitations"])


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------

class TestUValue:
    def test_two_layer_reference(self):
        """Single 100mm concrete layer (k=1.65):
        R = 0.13 + 0.04 + 0.1/1.65 = 0.230606 -> U = 4.3364 W/m2K
        """
        from src.modules.materials import MaterialLayer
        layers = [MaterialLayer("concrete", 100, 1.65, "test")]
        assert u_value_from_layers(layers) == pytest.approx(4.336, abs=0.01)

    def test_insulation_lowers_u_value(self):
        assert WALL_BRICK_INSULATED.u_value_w_m2k < WALL_150_BRICK_PLASTER.u_value_w_m2k
        assert ROOF_CONCRETE_INSULATED.u_value_w_m2k < ROOF_CONCRETE.u_value_w_m2k

    def test_u_values_in_physical_range(self):
        """Opaque assemblies should be 0.1 - 6 W/m2K."""
        for a in [WALL_150_BRICK_PLASTER, WALL_BRICK_INSULATED,
                  ROOF_CONCRETE, ROOF_CONCRETE_INSULATED]:
            assert 0.1 < a.u_value_w_m2k < 6.0

    def test_zero_thickness_layer_ignored(self):
        from src.modules.materials import MaterialLayer
        layers = [
            MaterialLayer("zero", 0, 0.04, "test"),
            MaterialLayer("brick", 150, 0.72, "test"),
        ]
        u = u_value_from_layers(layers)
        assert u > 0.0

    def test_insulated_wall_cheaper_than_code_target(self):
        """Insulated wall should approach the 2.0 W/m2K envelope intent."""
        assert WALL_BRICK_INSULATED.u_value_w_m2k < 1.0


class TestMaterialsDatabase:
    def test_all_assemblies_flagged_not_measured(self):
        m = list_assemblies()
        for a in m["opaque"]["assemblies"]:
            assert "derived" in a["verification"].lower() or "estimated" in a["verification"].lower()

    def test_every_assembly_has_source(self):
        m = list_assemblies()
        for a in m["opaque"]["assemblies"]:
            assert a["source_id"]
        for g in m["glazing"]["assemblies"]:
            assert g["source_id"]

    def test_limitation_declares_not_measured(self):
        m = list_assemblies()
        joined = " ".join(m["limitations"]).lower()
        assert "not measured" in joined

    def test_glazing_has_all_properties(self):
        for key, g in GLAZING_ASSEMBLIES.items():
            assert 0.0 < g["u_value_w_m2k"] < 10.0
            assert 0.0 < g["shgc"] <= 1.0
            assert 0.0 < g["vt"] <= 1.0

    def test_get_assembly_lookup(self):
        assert get_assembly("WALL-BRICK-150") is not None
        assert get_assembly("GLZ-CLEAR") is not None
        assert get_assembly("NOPE") is None


class TestEnvelopeSummary:
    def test_weighted_u_value_reference(self):
        """wall 100 m2 @ 2.413, roof 50 @ 4.069, glazing 20 @ 5.7
        total 170; weighted = (241.3 + 203.45 + 114) / 170 = 3.2868
        """
        r = envelope_summary(
            wall_area_m2=100, roof_area_m2=50, glazing_area_m2=20, glazing_type="Clear"
        )
        assert r["area_weighted_u_value_w_m2k"] == pytest.approx(3.287, abs=0.01)

    def test_zero_area_returns_insufficient(self):
        r = envelope_summary(wall_area_m2=0, roof_area_m2=0, glazing_area_m2=0)
        assert r["status"] == "Insufficient data"

    def test_glazing_fraction(self):
        r = envelope_summary(
            wall_area_m2=100, roof_area_m2=50, glazing_area_m2=20, glazing_type="Clear"
        )
        assert r["glazing_fraction_percent"] == pytest.approx(11.8, abs=0.2)

    def test_unknown_assembly_returns_insufficient(self):
        r = envelope_summary(wall_assembly_id="NOPE")
        assert r["status"] == "Insufficient data"

    def test_limitations_present(self):
        r = envelope_summary(wall_area_m2=100, roof_area_m2=50, glazing_area_m2=20)
        assert any("derived" in l.lower() for l in r["limitations"])