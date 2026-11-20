"""
Module P2-3 — Daylight Factor Screening (CIBSE / BRE average DF method).

Calculates the CIE overcast-sky Daylight Factor (DF) using the standard
"average daylight factor" method from CIBSE/SLL Lighting Guide 10 (LG10) and
BRE guidance.

    DF_avg (%) = (M x T x W x theta) / (A x (1 - R^2)) x 100

Where:
    M     = maintenance factor (default 0.8, CIBSE typical)
    T     = diffuse transmittance of glazing (dimensionless)
    W     = window area (m2)
    theta = visible sky angle in radians, subtended at the room centre by the
            window in the vertical plane normal to the facade
    A     = total internal surface area (m2) = floor + ceiling + walls
    R     = area-weighted mean reflectance of internal surfaces

Sky Component (SC), Externally Reflected Component (ERC) and Internally
Reflected Component (IRC) are combined in the standard method:
    DF_avg = SC + ERC + IRC
For screening with an unobstructed window we compute SC + IRC from the formula
above and report ERC as zero when no external obstruction is defined.

Engineering sources:
    - CIBSE/SLL Lighting Guide 10: Daylighting - a guide for designers
    - BRE Digest 309 / "Site layout planning for daylight and sunlight"
    - EN 17037 (daylight in buildings) for target values context only

IMPORTANT LIMITATIONS (always reported):
    - This is an analytical overcast-sky ESTIMATE, not a Radiance simulation.
    - No sDA/ASE, no hourly climate-based daylight modelling.
    - Assumes a rectangular room, uniform internal reflectance and a
      rectangular unobstructed window.
    - External obstructions are handled with a simple vertical sky-angle
      reduction, not a geometric shadow calculation.
"""
from __future__ import annotations

import math
from typing import Optional

from src.core.exceptions import ValidationFailure

# Maintenance factor (CIBSE typical for internal vertical glazing in a
# clean urban environment). Flagged as a screening assumption.
DEFAULT_MAINTENANCE_FACTOR = 0.8

# Diffuse visible transmittance by glazing type.
# Typical values from glazing manufacturer data / CIBSE LG10 tables.
# Flagged as screening assumptions; use manufacturer data when available.
GLAZING_TRANSMITTANCE = {
    "Clear": 0.85,          # single clear float glass
    "Tinted": 0.55,         # tinted solar-control glass
    "Double low-E": 0.72,   # double glazed, low-E coating
    "Other": 0.60,
}

# Default area-weighted internal reflectance (walls 0.5, ceiling 0.7,
# floor 0.2, area-weighted in a typical room).
DEFAULT_REFLECTANCE = 0.5

# EN 17037 / CIBSE target daylight factor context (NOT compliance claims).
DF_TARGET_BANDS = [
    (3.0, "Good daylight (DF >= 3%)"),
    (2.0, "Acceptable daylight (2% <= DF < 3%)"),
    (1.0, "Marginal daylight (1% <= DF < 2%)"),
    (0.0, "Poor daylight (DF < 1%)"),
]


def glazing_transmittance(glazing_type: str, custom_t: Optional[float] = None) -> float:
    """Resolve diffuse visible transmittance for a glazing type."""
    if custom_t is not None:
        if not (0.0 < custom_t <= 1.0):
            raise ValidationFailure("custom transmittance must be in (0, 1]")
        return custom_t
    return GLAZING_TRANSMITTANCE.get(glazing_type, GLAZING_TRANSMITTANCE["Other"])


def visible_sky_angle(
    window_width_m: float,
    window_height_m: float,
    room_length_m: float,
    room_width_m: float,
) -> float:
    """Estimate the visible sky angle theta (radians) at the room centre.

    Simplified CIBSE approach: the window is treated as a vertical rectangle
    on one wall, and theta is the angle subtended by its height at the room
    centre in the vertical plane normal to that wall.

        theta = 2 * atan( h_w / (2 * d) )

    where d is the perpendicular distance from the room centre to the window
    wall (half the room dimension normal to the facade).

    This is a documented simplification for screening; a full solid-angle
    integration is out of scope for the MVP.
    """
    if window_height_m <= 0:
        return 0.0
    if room_length_m <= 0 or room_width_m <= 0:
        raise ValidationFailure("room dimensions must be positive")
    # Distance from room centre to the window wall = half the dimension normal
    # to that wall. Use the larger half-dimension as a conservative estimate
    # when orientation is unknown.
    d = max(room_length_m, room_width_m) / 2.0
    if d <= 0:
        return 0.0
    return 2.0 * math.atan(window_height_m / (2.0 * d))


def internal_surface_area(
    room_length_m: float,
    room_width_m: float,
    room_height_m: float,
) -> float:
    """Total internal surface area A = floor + ceiling + 4 walls."""
    if room_length_m <= 0 or room_width_m <= 0 or room_height_m <= 0:
        raise ValidationFailure("room dimensions must be positive")
    floor = room_length_m * room_width_m
    ceiling = floor
    walls = 2.0 * (room_length_m + room_width_m) * room_height_m
    return floor + ceiling + walls


def average_daylight_factor(
    window_area_m2: float,
    window_width_m: float,
    window_height_m: float,
    room_length_m: float,
    room_width_m: float,
    room_height_m: float,
    glazing_type: str = "Clear",
    maintenance_factor: float = DEFAULT_MAINTENANCE_FACTOR,
    reflectance: float = DEFAULT_REFLECTANCE,
    custom_transmittance: Optional[float] = None,
    obstruction_height_m: float = 0.0,
    obstruction_distance_m: float = 0.0,
) -> dict:
    """Compute the average daylight factor using the CIBSE/BRE method.

    Returns DF in percent plus the component breakdown, an interpretation
    band, confidence and limitations.
    """
    # --- Input validation ---
    for name, value in [
        ("window_area_m2", window_area_m2),
        ("window_width_m", window_width_m),
        ("window_height_m", window_height_m),
        ("room_length_m", room_length_m),
        ("room_width_m", room_width_m),
        ("room_height_m", room_height_m),
    ]:
        if value is None or value <= 0:
            raise ValidationFailure(f"{name} must be positive (got {value})")

    if not (0.0 < maintenance_factor <= 1.0):
        raise ValidationFailure("maintenance_factor must be in (0, 1]")
    if not (0.0 <= reflectance < 1.0):
        raise ValidationFailure("reflectance must be in [0, 1)")
    if obstruction_height_m < 0 or obstruction_distance_m < 0:
        raise ValidationFailure("obstruction values must be non-negative")

    T = glazing_transmittance(glazing_type, custom_transmittance)
    W = window_area_m2
    A = internal_surface_area(room_length_m, room_width_m, room_height_m)
    theta = visible_sky_angle(window_width_m, window_height_m, room_length_m, room_width_m)

    # --- External obstruction reduction ---
    # If an obstruction is defined, reduce the visible sky angle by the
    # vertical angle it blocks from the room centre.
    obstruction_reduction = 0.0
    if obstruction_height_m > 0 and obstruction_distance_m > 0:
        blocked_angle = math.atan(obstruction_height_m / obstruction_distance_m)
        # Clamp so we never reduce below 5% of the unobstructed sky
        obstruction_reduction = min(blocked_angle, theta * 0.95)
    theta_eff = max(theta - obstruction_reduction, theta * 0.05)

    # --- Sky component + internally reflected component ---
    denom = A * (1.0 - reflectance ** 2)
    if denom <= 0:
        raise ValidationFailure("invalid internal surface configuration")

    df_fraction = (maintenance_factor * T * W * theta_eff) / denom
    df_percent = df_fraction * 100.0

    # --- Interpretation band ---
    band = DF_TARGET_BANDS[-1][1]
    for threshold, label in DF_TARGET_BANDS:
        if df_percent >= threshold:
            band = label
            break

    # --- Confidence ---
    confidence = "Medium confidence"
    limitations = [
        "Analytical CIE overcast-sky ESTIMATE, not a Radiance simulation.",
        "No sDA/ASE or climate-based daylight modelling.",
        "Rectangular room, uniform reflectance and unobstructed rectangular window assumed.",
    ]
    if obstruction_height_m > 0:
        confidence = "Low confidence"
        limitations.append(
            "External obstruction reduced sky angle with a simple vertical-angle "
            "model, not a geometric shadow calculation."
        )
    if df_percent < 1.0:
        confidence = "Low confidence"

    return {
        "method": "CIBSE/SLL LG10 average daylight factor (BRE method)",
        "daylight_factor_percent": round(df_percent, 3),
        "sky_component_percent": round(df_percent, 3),
        "externally_reflected_component_percent": 0.0,
        "internally_reflected_component_percent": 0.0,
        "combined_df_percent": round(df_percent, 3),
        "interpretation": band,
        "inputs": {
            "window_area_m2": W,
            "window_width_m": window_width_m,
            "window_height_m": window_height_m,
            "room_length_m": room_length_m,
            "room_width_m": room_width_m,
            "room_height_m": room_height_m,
            "internal_surface_area_m2": round(A, 2),
            "visible_sky_angle_rad": round(theta, 4),
            "effective_sky_angle_rad": round(theta_eff, 4),
            "glazing_type": glazing_type,
            "glazing_transmittance": T,
            "maintenance_factor": maintenance_factor,
            "mean_reflectance": reflectance,
        },
        "obstruction": {
            "height_m": obstruction_height_m,
            "distance_m": obstruction_distance_m,
            "blocked_angle_deg": round(math.degrees(obstruction_reduction), 2),
        },
        "confidence": confidence,
        "limitations": limitations,
    }


def df_to_lux_estimate(
    daylight_factor_percent: float,
    design_sky_illuminance_lux: float = 10000.0,
) -> dict:
    """Convert a daylight factor to an indicative interior illuminance.

    E_interior = DF/100 x E_sky_horizontal
    A design sky illuminance of 10,000 lux is the CIE overcast standard used
    for DF definition. This is an INDICATIVE lux estimate, not a simulation.
    """
    if daylight_factor_percent < 0:
        raise ValidationFailure("daylight factor must be non-negative")
    lux = (daylight_factor_percent / 100.0) * design_sky_illuminance_lux
    return {
        "daylight_factor_percent": round(daylight_factor_percent, 3),
        "design_sky_illuminance_lux": design_sky_illuminance_lux,
        "indicative_interior_illuminance_lux": round(lux, 1),
        "method": "E = DF/100 x E_sky (CIE overcast, 10,000 lux)",
        "limitations": [
            "Indicative value under a standard overcast sky, not a measured or simulated value.",
            "Not a substitute for a lighting simulation or site measurement.",
        ],
        "status": "Estimated",
    }