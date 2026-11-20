"""
Module P2-1 — Climate Data Service.

Fetches and caches real climate data from NASA POWER (satellite-derived,
0.5° x 0.625° resolution, free, CC BY 4.0 style attribution required).

Fallback chain (documented, never silent):
    1. NASA POWER API (primary, satellite-derived)
    2. Cached file in data/climate/ (offline)
    3. Dhaka EPW file (if present)
    4. BMD 1991-2020 normals (hardcoded, source SRC-020) -> flagged

IMPORTANT: Never silently substitute one dataset for another. The returned
payload always names the dataset actually used.

NASA POWER parameters used:
    T2M                - Temperature at 2m (C)
    T2M_MAX / T2M_MIN  - Max/min temperature (C)
    RH2M               - Relative humidity (%)
    WS2M               - Wind speed at 2m (m/s)
    ALLSKY_SFC_SW_DWN  - All-sky surface shortwave downward irradiance (kWh/m2/day)
    CLRSKY_SFC_SW_DWN  - Clear-sky surface shortwave downward irradiance (kWh/m2/day)
    ALLSKY_SFC_SW_DIFF - Diffuse irradiance (kWh/m2/day)
    ALLSKY_SFC_SW_DNI  - Direct normal irradiance (kWh/m2/day)

Units: NASA POWER returns temperature in Celsius, irradiance in kWh/m2/day
(morning-to-morning accumulation), wind in m/s.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
from urllib.request import urlopen

NASA_POWER_MONTHLY_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"

# NASA POWER parameter registry: (description, unit)
NASA_POWER_PARAMETERS: dict[str, tuple[str, str]] = {
    "T2M": ("Temperature at 2 m (monthly mean)", "deg C"),
    "T2M_MAX": ("Extreme maximum temperature at 2 m (period max)", "deg C"),
    "T2M_MIN": ("Extreme minimum temperature at 2 m (period min)", "deg C"),
    "RH2M": ("Relative humidity at 2 m", "%"),
    "WS2M": ("Wind speed at 2 m", "m/s"),
    "ALLSKY_SFC_SW_DWN": ("All-sky global horizontal irradiance", "kWh/m2/day"),
    "CLRSKY_SFC_SW_DWN": ("Clear-sky global horizontal irradiance", "kWh/m2/day"),
    "ALLSKY_SFC_SW_DIFF": ("All-sky diffuse horizontal irradiance", "kWh/m2/day"),
    "ALLSKY_SFC_SW_DNI": ("All-sky direct normal irradiance", "kWh/m2/day"),
}

# ENGINEERING WARNING: NASA POWER T2M_MAX/T2M_MIN are the extreme maximum and
# minimum over the aggregation period, NOT the mean daily maximum/minimum.
# Averaging them does NOT give the mean temperature. Always use T2M for mean
# temperature; treat T2M_MAX as a design/extreme condition only.
NASA_POWER_UNITS_NOTE = (
    "T2M is the monthly MEAN temperature. T2M_MAX/T2M_MIN are EXTREMES, not "
    "mean daily max/min; do not average them to derive mean temperature."
)

# BMD 1991-2020 Dhaka normals (SRC-020) - used only as flagged fallback.
# Source: Bangladesh Meteorological Department via NOAA; see
# https://en.wikipedia.org/wiki/Climate_of_Dhaka (1991-2020 normals).
BMD_DHAKA_NORMALS: dict[str, dict[str, float]] = {
    "T2M_MAX": {
        "JAN": 24.6, "FEB": 28.3, "MAR": 32.4, "APR": 33.9, "MAY": 33.6, "JUN": 32.8,
        "JUL": 32.1, "AUG": 32.3, "SEP": 32.4, "OCT": 31.9, "NOV": 29.7, "DEC": 26.1,
    },
    "T2M_MIN": {
        "JAN": 13.3, "FEB": 16.6, "MAR": 21.1, "APR": 24.0, "MAY": 24.9, "JUN": 26.3,
        "JUL": 26.4, "AUG": 26.5, "SEP": 26.0, "OCT": 24.1, "NOV": 19.5, "DEC": 15.2,
    },
    "RH2M": {
        "JAN": 71, "FEB": 64, "MAR": 62, "APR": 71, "MAY": 76, "JUN": 82,
        "JUL": 83, "AUG": 82, "SEP": 83, "OCT": 78, "NOV": 73, "DEC": 73,
    },
}

MONTH_NAMES = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
               "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


@dataclass
class ClimateDataset:
    """A climate dataset with full provenance."""

    dataset_id: str
    source_name: str
    source_url: str
    publisher: str
    resolution: str
    units: dict[str, str]
    latitude: float
    longitude: float
    period: str
    monthly: dict[str, dict[int, float]] = field(default_factory=dict)
    verification_status: str = "Verified"
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def get(self, parameter: str, month: int) -> Optional[float]:
        """Get a monthly value. Returns None if missing (never 0)."""
        series = self.monthly.get(parameter)
        if not series:
            return None
        return series.get(month)


def _cache_path(lat: float, lon: float) -> Path:
    base = Path(__file__).resolve().parents[2] / "data" / "climate"
    base.mkdir(parents=True, exist_ok=True)
    tag = f"{abs(lat):.2f}_{abs(lon):.2f}".replace(".", "p")
    return base / f"nasa_power_{tag}_monthly.json"


def fetch_nasa_power(
    latitude: float,
    longitude: float,
    start_year: int = 2005,
    end_year: int = 2024,
    use_cache: bool = True,
) -> ClimateDataset:
    """Fetch NASA POWER monthly normals for a location.

    Returns a ClimateDataset with provenance. On network failure, falls back to
    cache, then to BMD normals (flagged as 'Estimated').

    Raises:
        RuntimeError: only if no data source at all is available.
    """
    cache = _cache_path(latitude, longitude)
    params = list(NASA_POWER_PARAMETERS.keys())

    # 1. Cache
    if use_cache and cache.exists():
        try:
            with open(cache, "r", encoding="utf-8") as f:
                blob = json.load(f)
            return _dataset_from_payload(blob, latitude, longitude)
        except (json.JSONDecodeError, KeyError):
            pass  # corrupt cache -> refetch

    # 2. Network
    query = urlencode({
        "parameters": ",".join(params),
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "format": "JSON",
        "start": start_year,
        "end": end_year,
    })
    url = f"{NASA_POWER_MONTHLY_URL}?{query}"

    try:
        with urlopen(url, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        dataset = _dataset_from_nasa(payload, latitude, longitude, start_year, end_year)
        if use_cache:
            with open(cache, "w", encoding="utf-8") as f:
                json.dump(dataset.to_dict(), f, indent=2)
        return dataset
    except Exception as exc:  # noqa: BLE001 - deliberate broad fallback
        # 3. BMD flagged fallback
        return _bmd_fallback(latitude, longitude, reason=str(exc))


def _dataset_from_nasa(
    payload: dict, lat: float, lon: float, start: int, end: int
) -> ClimateDataset:
    """Parse NASA POWER monthly JSON into a ClimateDataset."""
    raw_params = payload["properties"]["parameter"]
    monthly: dict[str, dict[int, float]] = {}

    for param, series in raw_params.items():
        monthly[param] = {}
        for key, value in series.items():
            # Keys look like "201401" (YYYYMM) or "201413" (annual "13")
            if not isinstance(value, (int, float)):
                continue
            if len(key) != 6:
                continue
            month = int(key[4:6])
            if month == 13:  # annual average
                continue
            monthly[param][month] = float(value)

    return ClimateDataset(
        dataset_id="SRC-011",
        source_name="NASA POWER (Prediction Of Worldwide Energy Resources)",
        source_url="https://power.larc.nasa.gov/",
        publisher="NASA Langley Research Center",
        resolution="0.5 x 0.625 deg",
        units={k: v[1] for k, v in NASA_POWER_PARAMETERS.items()},
        latitude=lat,
        longitude=lon,
        period=f"{start}-{end}",
        monthly=monthly,
        verification_status="Verified",
        notes=(
            "Satellite/ reanalysis-derived, not a ground station measurement. "
            "Required attribution: NASA POWER Project funded through the NASA "
            "Earth Science/Applied Science Program."
        ),
    )


def _dataset_from_payload(blob: dict, lat: float, lon: float) -> ClimateDataset:
    """Rebuild a dataset from a cached JSON blob."""
    monthly = {
        param: {int(m): float(v) for m, v in series.items()}
        for param, series in blob.get("monthly", {}).items()
    }
    return ClimateDataset(
        dataset_id=blob.get("dataset_id", "SRC-011"),
        source_name=blob.get("source_name", "NASA POWER"),
        source_url=blob.get("source_url", "https://power.larc.nasa.gov/"),
        publisher=blob.get("publisher", "NASA Langley Research Center"),
        resolution=blob.get("resolution", "0.5 x 0.625 deg"),
        units=blob.get("units", {}),
        latitude=lat,
        longitude=lon,
        period=blob.get("period", "cached"),
        monthly=monthly,
        verification_status=blob.get("verification_status", "Verified"),
        notes=blob.get("notes", "Loaded from local cache."),
    )


def _bmd_fallback(lat: float, lon: float, reason: str) -> ClimateDataset:
    """Return flagged BMD normals when NASA POWER is unavailable."""
    monthly: dict[str, dict[int, float]] = {}
    for param, by_month in BMD_DHAKA_NORMALS.items():
        monthly[param] = {}
        for idx, name in enumerate(MONTH_NAMES, start=1):
            monthly[param][idx] = float(by_month[name])

    return ClimateDataset(
        dataset_id="SRC-020",
        source_name="BMD 1991-2020 Dhaka climate normals (fallback)",
        source_url="https://en.wikipedia.org/wiki/Climate_of_Dhaka",
        publisher="Bangladesh Meteorological Department / NOAA",
        resolution="station (Dhaka)",
        units={"T2M_MAX": "deg C", "T2M_MIN": "deg C", "RH2M": "%"},
        latitude=lat,
        longitude=lon,
        period="1991-2020",
        monthly=monthly,
        verification_status="Partially verified",
        notes=(
            f"Fallback used because NASA POWER was unavailable: {reason}. "
            "Only temperature and humidity are available; solar irradiance "
            "parameters are absent, so solar/daylight modules must report "
            "'Insufficient data'."
        ),
    )


def climate_summary(dataset: ClimateDataset) -> dict:
    """Produce a compact summary for the UI/report."""
    tmean = dataset.monthly.get("T2M", {})
    txmax = dataset.monthly.get("T2M_MAX", {})
    txmin = dataset.monthly.get("T2M_MIN", {})
    ghi = dataset.monthly.get("ALLSKY_SFC_SW_DWN", {})

    summary = {
        "dataset_id": dataset.dataset_id,
        "source_name": dataset.source_name,
        "period": dataset.period,
        "resolution": dataset.resolution,
        "verification_status": dataset.verification_status,
        "annual_mean_temp_c": None,
        "extreme_max_temp_c": None,
        "extreme_min_temp_c": None,
        "annual_mean_ghi_kwh_m2_day": None,
        "months": {},
        "engineering_notes": [NASA_POWER_UNITS_NOTE],
        "limitations": [],
    }

    if tmean:
        summary["annual_mean_temp_c"] = round(sum(tmean.values()) / len(tmean), 2)
    if txmax:
        summary["extreme_max_temp_c"] = round(max(txmax.values()), 2)
    if txmin:
        summary["extreme_min_temp_c"] = round(min(txmin.values()), 2)
    if ghi:
        summary["annual_mean_ghi_kwh_m2_day"] = round(sum(ghi.values()) / len(ghi), 3)

    for m in range(1, 13):
        summary["months"][m] = {
            "name": MONTH_NAMES[m - 1],
            "tmean_c": tmean.get(m),
            "extreme_max_c": txmax.get(m),
            "extreme_min_c": txmin.get(m),
            "ghi_kwh_m2_day": ghi.get(m),
        }

    if not ghi:
        summary["limitations"].append(
            "Solar irradiance unavailable in this dataset; solar and daylight "
            "modules cannot be evaluated."
        )
    summary["limitations"].append(
        "Monthly normals, not hourly data; use for screening, not simulation."
    )
    return summary


def cooling_degree_days(dataset: ClimateDataset, base_c: float = 26.0) -> dict:
    """Cooling degree days from monthly MEAN temperature (T2M).

    CDD = sum over months of max(0, Tmean - base) * days_in_month.
    Uses T2M (true monthly mean), NOT an average of extremes.
    """
    tmean = dataset.monthly.get("T2M", {})
    if not tmean:
        return {"available": False, "cdd_base_c": base_c, "cdd_total": None,
                "limitations": ["Mean temperature (T2M) unavailable."]}

    days = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthly: dict[int, float] = {}
    total = 0.0
    for m in range(1, 13):
        if m not in tmean:
            continue
        cdd = max(0.0, tmean[m] - base_c) * days[m - 1]
        monthly[m] = round(cdd, 1)
        total += cdd

    return {
        "available": True,
        "cdd_base_c": base_c,
        "cdd_total": round(total, 1),
        "monthly": monthly,
        "method": "sum(max(0, T2M_mean - base) x days_in_month)",
        "limitations": [
            "Approximated from monthly mean normals; hourly integration is more accurate.",
            f"Base temperature {base_c} C is a screening assumption, not a code requirement.",
        ],
    }