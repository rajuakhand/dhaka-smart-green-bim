"""
Module P2-2 — Solar Geometry and Solar Heat Gain.

Uses pvlib (peer-reviewed, NREL SPA algorithm by Reda & Andreas) for solar
position, and the Ineichen-Perez clear-sky model for irradiance. All values
are CALCULATED from astronomical geometry and a documented model — they are
NOT measured and NOT full-year simulation.

Engineering basis:
  - Solar position: NREL SPA (Reda & Andreas 2004), implemented in pvlib.
  - Clear-sky irradiance: Ineichen & Perez (2002) as implemented in pvlib.
  - Surface transposition: pvlib.irradiance.get_total_irradiance (Hay-Davies).
  - Solar heat gain through glazing: Q = A_glass x I_solar x SHGC.
  - Solar profile angle: tan(p) = tan(altitude) / cos(surface_azimuth - solar_azimuth)

Units:
  - Latitude/longitude: decimal degrees
  - Irradiance: W/m2
  - Temperature: deg C
  - Times: timezone-aware pandas DatetimeIndex

Limitations (always reported):
  - Clear-sky model, not measured sky conditions.
  - No hourly simulation of the building; single-point / daily aggregation.
  - SHGC and frame factors are user assumptions unless a material is selected.
"""
from __future__ import annotations

from typing import Optional

import pandas as pd

try:
    from pvlib import solarposition, clearsky, irradiance, atmosphere
    from pvlib.location import Location

    PVLIB_AVAILABLE = True
    PVLIB_IMPORT_ERROR = ""
except Exception as exc:  # noqa: BLE001
    PVLIB_AVAILABLE = False
    PVLIB_IMPORT_ERROR = str(exc)

# Dhaka reference location (SRC-011 / BMD). Used as the default study site.
DHAKA_LATITUDE = 23.8103
DHAKA_LONGITUDE = 90.4125
DHAKA_ALTITUDE_M = 4.0
DHAKA_TIMEZONE = "Asia/Dhaka"

# Default glazing solar heat gain coefficients (SHGC) by type.
# These are typical mid-range values for screening; manufacturer data should
# be substituted when available. Source: ASHRAE Fundamentals / CIBSE Guide A
# typical ranges, flagged as screening assumptions.
DEFAULT_SHGC = {
    "Clear": 0.82,          # single clear glazing, typical
    "Tinted": 0.55,         # bronze/grey tinted
    "Double low-E": 0.35,   # double glazed with low-E coating
    "Other": 0.60,
}

# Orientation labels for compass degrees
COMPASS_LABELS = [
    (0.0, "North"), (45.0, "North-East"), (90.0, "East"), (135.0, "South-East"),
    (180.0, "South"), (225.0, "South-West"), (270.0, "West"), (315.0, "North-West"),
    (360.0, "North"),
]


def compass_label(azimuth_deg: float) -> str:
    """Convert an azimuth in degrees to a compass label."""
    az = azimuth_deg % 360.0
    best = min(COMPASS_LABELS, key=lambda pair: min(abs(az - pair[0]), 360 - abs(az - pair[0])))
    return best[1]


def _require_pvlib():
    if not PVLIB_AVAILABLE:
        raise RuntimeError(
            "pvlib is required for solar geometry calculations but is not "
            f"installed. Import error: {PVLIB_IMPORT_ERROR}. "
            "Install with: pip install pvlib"
        )


def solar_position(
    latitude: float,
    longitude: float,
    times: pd.DatetimeIndex,
    altitude: float = 0.0,
    timezone: str = DHAKA_TIMEZONE,
) -> pd.DataFrame:
    """Calculate solar position (apparent zenith, azimuth) for given times.

    Returns DataFrame with columns: apparent_zenith, zenith, azimuth,
    equation_of_time.
    """
    _require_pvlib()
    location = Location(latitude=latitude, longitude=longitude, tz=timezone, altitude=altitude)
    times = times.tz_localize(timezone) if times.tz is None else times.tz_convert(timezone)
    return location.get_solarposition(times)


def clear_sky_irradiance(
    latitude: float,
    longitude: float,
    times: pd.DatetimeIndex,
    altitude: float = 0.0,
    timezone: str = DHAKA_TIMEZONE,
    model: str = "ineichen",
) -> pd.DataFrame:
    """Calculate clear-sky GHI, DNI, DHI for given times.

    model: 'ineichen' (Ineichen-Perez, default) or 'haurwitz' (simpler).
    """
    _require_pvlib()
    location = Location(latitude=latitude, longitude=longitude, tz=timezone, altitude=altitude)
    times = times.tz_localize(timezone) if times.tz is None else times.tz_convert(timezone)
    solpos = location.get_solarposition(times)
    zenith = solpos["apparent_zenith"]
    # pvlib >= 0.16: airmass is derived in two steps (relative -> absolute)
    am_rel = atmosphere.get_relative_airmass(zenith).fillna(1e6)
    pressure = float(atmosphere.alt2press(altitude)) if hasattr(atmosphere, "alt2press") \
        else float(atmosphere.alt2pres(altitude))
    am_abs = atmosphere.get_absolute_airmass(am_rel, pressure=pressure)

    if model == "haurwitz":
        sky = clearsky.haurwitz(zenith)
    else:
        try:
            linke = clearsky.lookup_linke_turbidity(times, latitude, longitude)
        except Exception:  # noqa: BLE001 - documented typical value fallback
            linke = 3.0
        sky = clearsky.ineichen(zenith, am_abs, linke, altitude=altitude)
    return sky


def surface_irradiance(
    latitude: float,
    longitude: float,
    times: pd.DatetimeIndex,
    surface_azimuth_deg: float,
    surface_tilt_deg: float = 90.0,
    albedo: float = 0.2,
    altitude: float = 0.0,
    timezone: str = DHAKA_TIMEZONE,
) -> pd.DataFrame:
    """Calculate total solar irradiance on a tilted surface.

    surface_azimuth_deg: 0=N, 90=E, 180=S, 270=W (pvlib convention).
    surface_tilt_deg: 90 = vertical wall (default), 0 = horizontal.
    Returns DataFrame with poa_global, poa_direct, poa_diffuse, poa_sky_diffuse,
    poa_ground_diffuse in W/m2.
    """
    _require_pvlib()
    location = Location(latitude=latitude, longitude=longitude, tz=timezone, altitude=altitude)
    times = times.tz_localize(timezone) if times.tz is None else times.tz_convert(timezone)
    solpos = location.get_solarposition(times)
    sky = clear_sky_irradiance(latitude, longitude, times, altitude, timezone)

    total = irradiance.get_total_irradiance(
        surface_tilt=surface_tilt_deg,
        surface_azimuth=surface_azimuth_deg,
        solar_zenith=solpos["apparent_zenith"],
        solar_azimuth=solpos["azimuth"],
        dni=sky["dni"],
        ghi=sky["ghi"],
        dhi=sky["dhi"],
        albedo=albedo,
    )
    return total


def solar_profile_angle(
    solar_altitude_deg: float,
    solar_azimuth_deg: float,
    surface_azimuth_deg: float,
) -> float:
    """Solar profile angle (degrees) on a vertical surface.

    tan(profile) = tan(altitude) / cos(surface_azimuth - solar_azimuth)
    Profile angle is the angle of the sun above the facade plane.
    """
    import math

    if solar_altitude_deg <= 0:
        return 0.0
    delta = math.radians(surface_azimuth_deg - solar_azimuth_deg)
    cos_delta = math.cos(delta)
    if cos_delta <= 0:
        return 0.0  # sun behind the facade
    alt = math.radians(solar_altitude_deg)
    return math.degrees(math.atan(math.tan(alt) / cos_delta))


def daily_sun_path(
    latitude: float,
    longitude: float,
    date: pd.Timestamp,
    timezone: str = DHAKA_TIMEZONE,
    altitude: float = 0.0,
) -> dict:
    """Compute the sun path for a single day at 15-minute resolution."""
    _require_pvlib()
    times = pd.date_range(
        start=pd.Timestamp(date).normalize(),
        periods=96,
        freq="15min",
        tz=timezone,
    )
    pos = solar_position(latitude, longitude, times, altitude, timezone)
    pos = pos.reset_index()
    pos["time_str"] = pos.iloc[:, 0].dt.strftime("%H:%M")
    samples = []
    for _, row in pos.iterrows():
        zenith = float(row["apparent_zenith"])
        samples.append({
            "time": row["time_str"],
            "altitude_deg": round(90.0 - zenith, 3),
            "zenith_deg": round(zenith, 3),
            "azimuth_deg": round(float(row["azimuth"]), 3),
            "compass": compass_label(float(row["azimuth"])),
        })
    daylight = [s for s in samples if s["altitude_deg"] > 0]
    peak = max(daylight, key=lambda s: s["altitude_deg"]) if daylight else None
    return {
        "date": str(pd.Timestamp(date).date()),
        "latitude": latitude,
        "longitude": longitude,
        "samples": samples,
        "daylight_hours": round(len(daylight) * 0.25, 2),
        "peak_altitude_deg": peak["altitude_deg"] if peak else None,
        "peak_time": peak["time"] if peak else None,
        "method": "NREL SPA via pvlib, 15-minute resolution",
        "limitations": [
            "Clear-sky geometry only; no cloud cover modelling.",
            "Local horizon/terrain not considered.",
        ],
    }


def facade_solar_summary(
    latitude: float,
    longitude: float,
    building_orientation_deg: float,
    date: pd.Timestamp = pd.Timestamp("2026-06-21"),
    altitude: float = 0.0,
    timezone: str = DHAKA_TIMEZONE,
) -> dict:
    """Summarise solar exposure for the four cardinal facades of a building.

    building_orientation_deg: the direction the main facade faces (0=N).
    Returns per-facade daily total POA irradiance (kWh/m2/day) and peak.
    """
    _require_pvlib()
    times = pd.date_range(
        start=pd.Timestamp(date).normalize(), periods=96, freq="15min", tz=timezone
    )
    base = building_orientation_deg
    facades = {
        "Front": base,
        "Right": (base + 90) % 360,
        "Rear": (base + 180) % 360,
        "Left": (base + 270) % 360,
    }

    results: dict[str, dict] = {}
    for name, az in facades.items():
        total = surface_irradiance(
            latitude, longitude, times, surface_azimuth_deg=az,
            surface_tilt_deg=90.0, altitude=altitude, timezone=timezone,
        )
        poa = total["poa_global"].clip(lower=0)
        # 15-minute samples -> kWh/m2 = sum(W/m2 * 0.25h) / 1000
        daily_kwh = float(poa.sum() * 0.25 / 1000.0)
        results[name] = {
            "azimuth_deg": round(az, 1),
            "compass": compass_label(az),
            "daily_poa_kwh_m2": round(daily_kwh, 3),
            "peak_poa_w_m2": round(float(poa.max()), 1),
        }

    ranked = sorted(results.items(), key=lambda kv: kv[1]["daily_poa_kwh_m2"], reverse=True)
    return {
        "date": str(pd.Timestamp(date).date()),
        "building_orientation_deg": building_orientation_deg,
        "facades": results,
        "highest_exposure_facade": ranked[0][0],
        "lowest_exposure_facade": ranked[-1][0],
        "method": "pvlib Ineichen-Perez clear-sky + Hay-Davies transposition",
        "limitations": [
            "Clear-sky irradiance, not measured weather.",
            "No shading from adjacent buildings (see shading module).",
            "Vertical surfaces only (tilt=90).",
        ],
    }


def solar_heat_gain(
    glass_area_m2: float,
    incident_irradiance_w_m2: float,
    shgc: float,
    shading_factor: float = 1.0,
) -> dict:
    """Instantaneous solar heat gain through glazing.

    Q_gain = A_glass x I_incident x SHGC x shading_factor   [W]
    """
    if glass_area_m2 < 0:
        raise ValueError("glass_area_m2 must be non-negative")
    if incident_irradiance_w_m2 < 0:
        raise ValueError("incident_irradiance_w_m2 must be non-negative")
    if not (0.0 <= shgc <= 1.0):
        raise ValueError("shgc must be between 0 and 1")
    if not (0.0 <= shading_factor <= 1.0):
        raise ValueError("shading_factor must be between 0 and 1")

    gain_w = glass_area_m2 * incident_irradiance_w_m2 * shgc * shading_factor
    return {
        "glass_area_m2": glass_area_m2,
        "incident_irradiance_w_m2": round(incident_irradiance_w_m2, 2),
        "shgc": shgc,
        "shading_factor": shading_factor,
        "solar_heat_gain_w": round(gain_w, 2),
        "solar_heat_gain_kw": round(gain_w / 1000.0, 4),
        "method": "Q = A x I x SHGC x shading_factor",
        "limitations": [
            "SHGC is a screening assumption unless a manufacturer value is supplied.",
            "No thermal mass or time-lag modelling.",
            "Instantaneous value, not an annual total.",
        ],
    }


def shgc_for_glazing(glazing_type: str, custom_shgc: Optional[float] = None) -> float:
    """Resolve an SHGC for a glazing type."""
    if custom_shgc is not None:
        if not (0.0 <= custom_shgc <= 1.0):
            raise ValueError("custom_shgc must be between 0 and 1")
        return custom_shgc
    return DEFAULT_SHGC.get(glazing_type, DEFAULT_SHGC["Other"])