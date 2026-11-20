"""
Module P2-4 — Advanced Shading Analysis.

Geometric shading calculations for:
    - Overhangs and vertical fins on a facade
    - Obstructions from adjacent buildings (simple box model)
    - Required shading depth to cut direct sun on a given date
    - Shadow length from a given obstruction

Method basis:
    - Solar profile angle: tan(p) = tan(altitude) / cos(surface_azimuth - solar_azimuth)
    - Required overhang depth for full shade: d = h / tan(p)
    - Shadow length on the ground: L = H / tan(altitude)
    - Vertical shadow angle (VSA) and horizontal shadow angle (HSA) per
      BRE/CIBSE sun-path geometry.

This is geometric analysis using the NREL SPA solar position (via pvlib).
It is CALCULATED geometry, not a rendered shadow simulation.

Limitations (always reported):
    - Box-model obstructions only; complex geometry not handled.
    - No diffuse sky shading from an obstruction.
    - Single date/time, not an annual shade fraction.
"""
from __future__ import annotations

import math
from typing import Optional

import pandas as pd

from src.core.exceptions import ValidationFailure
from src.modules.solar_geometry import (
    DHAKA_LATITUDE,
    DHAKA_LONGITUDE,
    DHAKA_TIMEZONE,
    solar_position,
    solar_profile_angle,
)


def shadow_length(obstruction_height_m: float, solar_altitude_deg: float) -> float:
    """Ground shadow length cast by an obstruction of height H.

    L = H / tan(altitude). Returns 0 when the sun is at or below the horizon
    and float('inf') is never returned (a very low sun gives a very long,
    finite shadow that is capped).
    """
    if obstruction_height_m < 0:
        raise ValidationFailure("obstruction_height_m must be non-negative")
    if solar_altitude_deg <= 0.5:
        return 0.0
    return obstruction_height_m / math.tan(math.radians(solar_altitude_deg))


def required_overhang_depth(
    window_height_m: float,
    profile_angle_deg: float,
) -> float:
    """Overhang depth needed to fully shade a window of height h.

    d = h / tan(profile_angle)
    Returns 0.0 if the sun is behind the facade (profile angle 0).
    """
    if window_height_m <= 0:
        raise ValidationFailure("window_height_m must be positive")
    if profile_angle_deg <= 0.5:
        return 0.0
    return window_height_m / math.tan(math.radians(profile_angle_deg))


def overhang_shaded_fraction(
    window_height_m: float,
    overhang_depth_m: float,
    profile_angle_deg: float,
) -> dict:
    """Fraction of a window shaded by a horizontal overhang.

    shaded_height = overhang_depth * tan(profile_angle)
    shaded_fraction = min(shaded_height / window_height, 1)
    """
    if window_height_m <= 0:
        raise ValidationFailure("window_height_m must be positive")
    if overhang_depth_m < 0:
        raise ValidationFailure("overhang_depth_m must be non-negative")

    if profile_angle_deg <= 0.5:
        shaded_height = 0.0
    else:
        shaded_height = overhang_depth_m * math.tan(math.radians(profile_angle_deg))

    fraction = min(shaded_height / window_height_m, 1.0)
    return {
        "window_height_m": window_height_m,
        "overhang_depth_m": overhang_depth_m,
        "profile_angle_deg": round(profile_angle_deg, 2),
        "shaded_height_m": round(shaded_height, 3),
        "shaded_fraction": round(fraction, 3),
        "shaded_percent": round(fraction * 100.0, 1),
        "fully_shaded": fraction >= 1.0,
        "method": "shaded_height = overhang_depth * tan(profile_angle)",
    }


def fin_shaded_fraction(
    window_width_m: float,
    fin_depth_m: float,
    horizontal_shadow_angle_deg: float,
) -> dict:
    """Fraction of a window shaded by a vertical fin.

    shaded_width = fin_depth * tan(HSA)
    """
    if window_width_m <= 0:
        raise ValidationFailure("window_width_m must be positive")
    if fin_depth_m < 0:
        raise ValidationFailure("fin_depth_m must be non-negative")

    if horizontal_shadow_angle_deg <= 0.5:
        shaded_width = 0.0
    else:
        shaded_width = fin_depth_m * math.tan(math.radians(horizontal_shadow_angle_deg))

    fraction = min(shaded_width / window_width_m, 1.0)
    return {
        "window_width_m": window_width_m,
        "fin_depth_m": fin_depth_m,
        "horizontal_shadow_angle_deg": round(horizontal_shadow_angle_deg, 2),
        "shaded_width_m": round(shaded_width, 3),
        "shaded_fraction": round(fraction, 3),
        "shaded_percent": round(fraction * 100.0, 1),
        "fully_shaded": fraction >= 1.0,
        "method": "shaded_width = fin_depth * tan(HSA)",
    }


def facade_shading_analysis(
    latitude: float = DHAKA_LATITUDE,
    longitude: float = DHAKA_LONGITUDE,
    facade_azimuth_deg: float = 180.0,
    window_height_m: float = 1.5,
    window_width_m: float = 2.0,
    overhang_depth_m: float = 0.0,
    fin_depth_m: float = 0.0,
    date: Optional[pd.Timestamp] = None,
    obstruction_distance_m: float = 0.0,
    obstruction_height_m: float = 0.0,
) -> dict:
    """Analyse shading on a facade for a given date at 30-minute resolution.

    facade_azimuth_deg: direction the facade faces (0=N, 180=S).
    Returns hourly shading profile plus design recommendations.
    """
    for name, value in [
        ("window_height_m", window_height_m),
        ("window_width_m", window_width_m),
    ]:
        if value <= 0:
            raise ValidationFailure(f"{name} must be positive")
    if overhang_depth_m < 0 or fin_depth_m < 0:
        raise ValidationFailure("shading depths must be non-negative")
    if obstruction_distance_m < 0 or obstruction_height_m < 0:
        raise ValidationFailure("obstruction values must be non-negative")

    date = date or pd.Timestamp("2026-06-21")
    times = pd.date_range(
        start=pd.Timestamp(date).normalize(), periods=48, freq="30min", tz=DHAKA_TIMEZONE
    )
    pos = solar_position(latitude, longitude, times)

    samples: list[dict] = []
    for ts, row in pos.iterrows():
        altitude = 90.0 - float(row["apparent_zenith"])
        azimuth = float(row["azimuth"])
        if altitude <= 0:
            samples.append({
                "time": ts.strftime("%H:%M"),
                "altitude_deg": 0.0,
                "azimuth_deg": round(azimuth, 1),
                "sun_on_facade": False,
                "profile_angle_deg": 0.0,
                "hsa_deg": 0.0,
                "overhang_shaded_percent": 0.0,
                "fin_shaded_percent": 0.0,
            })
            continue

        profile = solar_profile_angle(altitude, azimuth, facade_azimuth_deg)
        # Horizontal shadow angle: angle in plan between facade normal and sun
        delta = math.radians(azimuth - facade_azimuth_deg)
        # Only when the sun is in front of the facade (|delta| < 90)
        sun_on_facade = abs(math.degrees(delta)) < 90.0
        hsa = abs(math.degrees(delta)) if sun_on_facade else 0.0

        oh = overhang_shaded_fraction(window_height_m, overhang_depth_m, profile) if sun_on_facade else {
            "shaded_percent": 0.0
        }
        fin = fin_shaded_fraction(window_width_m, fin_depth_m, hsa) if sun_on_facade else {
            "shaded_percent": 0.0
        }

        samples.append({
            "time": ts.strftime("%H:%M"),
            "altitude_deg": round(altitude, 2),
            "azimuth_deg": round(azimuth, 1),
            "sun_on_facade": sun_on_facade,
            "profile_angle_deg": round(profile, 2),
            "hsa_deg": round(hsa, 2),
            "overhang_shaded_percent": oh["shaded_percent"],
            "fin_shaded_percent": fin["shaded_percent"],
        })

    sunlit = [s for s in samples if s["sun_on_facade"] and s["altitude_deg"] > 0]
    peak_profile = max((s["profile_angle_deg"] for s in sunlit), default=0.0)

    # Obstruction screening: does a neighbouring block the window?
    obstruction = None
    if obstruction_height_m > 0 and obstruction_distance_m > 0:
        # Vertical angle blocked from the window centre
        v_angle = math.degrees(math.atan(obstruction_height_m / obstruction_distance_m))
        obstruction = {
            "height_m": obstruction_height_m,
            "distance_m": obstruction_distance_m,
            "vertical_blocking_angle_deg": round(v_angle, 2),
            "ground_shadow_length_m": round(shadow_length(obstruction_height_m, peak_profile or 45.0), 2),
            "screening_note": (
                "If this vertical blocking angle exceeds the solar profile angle, "
                "direct sun is blocked for that time step."
            ),
        }

    # Recommendations
    recommendations: list[str] = []
    is_east_west = min(
        abs(facade_azimuth_deg - 90.0), abs(facade_azimuth_deg - 270.0)
    ) < 22.5

    if is_east_west:
        if fin_depth_m == 0:
            recommendations.append(
                "East/West facades receive low-angle morning/evening sun. Vertical "
                "fins are more effective than horizontal overhangs on this orientation; "
                "consider external shading, vegetation, or reduced glazing."
            )
    elif overhang_depth_m == 0 and 15 < peak_profile < 85:
        need = required_overhang_depth(window_height_m, peak_profile)
        recommendations.append(
            f"Consider an overhang of about {need:.2f} m to shade the window at "
            f"the peak profile angle of {peak_profile:.1f} deg."
        )

    if len(sunlit) * 0.5 < 1.0:
        recommendations.append(
            "This facade is largely self-shaded on the analysed date; shading "
            "devices will have limited benefit for this orientation/season."
        )
    if not recommendations:
        recommendations.append(
            "Existing shading is adequate for the analysed date and orientation."
        )

    return {
        "date": str(pd.Timestamp(date).date()),
        "facade_azimuth_deg": facade_azimuth_deg,
        "facade_orientation": _compass(facade_azimuth_deg),
        "window": {"height_m": window_height_m, "width_m": window_width_m},
        "shading": {"overhang_depth_m": overhang_depth_m, "fin_depth_m": fin_depth_m},
        "samples": samples,
        "sunlit_hours": round(len(sunlit) * 0.5, 2),
        "peak_profile_angle_deg": round(peak_profile, 2),
        "required_overhang_for_peak_m": round(required_overhang_depth(window_height_m, peak_profile), 3),
        "obstruction": obstruction,
        "recommendations": recommendations,
        "method": "Geometric shading using NREL SPA solar position (pvlib)",
        "limitations": [
            "Box-model obstructions only; complex geometry not handled.",
            "No diffuse sky shading from obstructions.",
            "Single design date, not an annual shade fraction.",
            "Profile-angle method assumes a flat vertical facade.",
        ],
        "status": "Estimated",
        "confidence": "Medium confidence" if not obstruction else "Low confidence",
    }


def _compass(azimuth_deg: float) -> str:
    from src.modules.solar_geometry import compass_label
    return compass_label(azimuth_deg)