"""
Domain models for DhakaSmart platform.

All Pydantic models include field validators so malformed input is rejected
before any calculation runs. Units are declared in field descriptions.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ConfidenceLevel(str, Enum):
    """Confidence categories (no invented percentages)."""

    HIGH = "High confidence"
    MEDIUM = "Medium confidence"
    LOW = "Low confidence"
    INSUFFICIENT = "Insufficient data"


class ResultStatus(str, Enum):
    """Status indicators used across all result screens."""

    VERIFIED = "Verified"
    ESTIMATED = "Estimated"
    SIMULATED = "Simulated"
    NOT_EVALUATED = "Not evaluated"
    INSUFFICIENT_DATA = "Insufficient data"
    NEEDS_REVIEW = "Needs professional review"


class BuildingType(str, Enum):
    RESIDENTIAL = "Residential"
    MIXED_USE = "Mixed-use"
    OFFICE = "Office"
    COMMERCIAL = "Commercial"
    INDUSTRIAL = "Industrial"
    INSTITUTIONAL = "Institutional"
    OTHER = "Other"


class StructuralSystem(str, Enum):
    FRAME = "Frame"
    SHEAR_WALL = "Shear-wall"
    MOMENT_RESISTING = "Moment-resisting"
    MASONRY = "Masonry"
    LOAD_BRICK = "Load-bearing brick"
    UNKNOWN = "Unknown"


class RoomType(str, Enum):
    RESIDENTIAL = "Residential"
    OFFICE = "Office"
    CLASSROOM = "Classroom"
    HOSPITAL = "Hospital"
    RETAIL = "Retail"
    STORAGE = "Storage"
    LABORATORY = "Laboratory"
    ASSEMBLY = "Assembly"
    OTHER = "Other"


class OccupancySchedule(str, Enum):
    DAYTIME = "Daytime"
    EVENING = "Evening"
    TWENTY_FOUR_HOUR = "24hr"
    CUSTOM = "Custom"


class GlazingType(str, Enum):
    CLEAR = "Clear"
    TINTED = "Tinted"
    DOUBLE_LOW_E = "Double low-E"
    OTHER = "Other"


class ShadingType(str, Enum):
    NONE = "None"
    OVERHANG = "Overhang"
    FIN = "Fin"
    BOTH = "Both"


class EmissionFactorSource(str, Enum):
    DOE_GEF = "DoE-GEF"
    EMBER_OWID = "Ember-OWID"
    USER_SUPPLIED = "User-supplied"


# ---------------------------------------------------------------------------
# Module A — Building
# ---------------------------------------------------------------------------

class BuildingBase(BaseModel):
    """Shared building fields."""

    name: str = Field(min_length=1, max_length=200, description="Project name")
    building_name: Optional[str] = Field(default=None, max_length=200)
    city: str = Field(default="Dhaka", max_length=100)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="Degrees N")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="Degrees E")
    building_type: BuildingType
    num_floors: int = Field(ge=1, le=50, description="Storeys above ground")
    floor_to_floor_height_m: float = Field(ge=2.0, le=6.0, description="Floor-to-floor height (m)")
    orientation_deg: float = Field(
        default=0.0, ge=0, le=360,
        description="Primary facade orientation, degrees clockwise from North (0=N, 90=E, 180=S, 270=W)",
    )
    construction_year: Optional[int] = Field(default=None, ge=1900, le=2100)
    structural_system: Optional[StructuralSystem] = Field(default=None)
    plot_area_m2: Optional[float] = Field(default=None, gt=0, description="Plot area (m²)")
    building_footprint_m2: Optional[float] = Field(default=None, gt=0, description="Footprint (m²)")

    @field_validator("latitude")
    @classmethod
    def _valid_lat(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def _valid_lon(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("longitude must be between -180 and 180")
        return v


class BuildingCreate(BuildingBase):
    """Payload for creating a project."""


class Building(BuildingBase):
    """Building persisted with identifiers."""

    id: UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Module B — Room
# ---------------------------------------------------------------------------

class RoomBase(BaseModel):
    """Shared room fields."""

    name: str = Field(min_length=1, max_length=100)
    room_type: RoomType
    length_m: float = Field(ge=1.0, le=50.0, description="Length (m)")
    width_m: float = Field(ge=1.0, le=50.0, description="Width (m)")
    height_m: float = Field(ge=2.0, le=15.0, description="Ceiling height (m)")
    window_area_m2: float = Field(default=0.0, ge=0, description="Total glazed area (m²)")
    openable_window_area_m2: float = Field(default=0.0, ge=0, description="Effective openable area (m²)")
    occupants: int = Field(ge=1, le=100)
    occupancy_schedule: Optional[OccupancySchedule] = Field(default=None)
    orientation_deg: Optional[float] = Field(default=None, ge=0, le=360, description="0=N")
    glazing_type: Optional[GlazingType] = Field(default=None)
    external_obstruction_height_m: float = Field(default=0.0, ge=0, description="Adjacent obstruction height (m)")
    shading_type: Optional[ShadingType] = Field(default=None)

    @model_validator(mode="after")
    def _validate_geometry(self) -> "RoomBase":
        if self.openable_window_area_m2 > self.window_area_m2:
            raise ValueError(
                f"openable area ({self.openable_window_area_m2}) cannot exceed "
                f"total window area ({self.window_area_m2})"
            )
        return self

    @property
    def floor_area_m2(self) -> float:
        return round(self.length_m * self.width_m, 3)

    @property
    def volume_m3(self) -> float:
        return round(self.floor_area_m2 * self.height_m, 3)

    @property
    def wall_area_m2(self) -> float:
        """Exterior wall area approximated by perimeter × height (4 walls)."""
        perimeter = 2 * (self.length_m + self.width_m)
        return round(perimeter * self.height_m, 3)


class RoomCreate(RoomBase):
    """Payload for creating a room."""


class Room(RoomBase):
    """Room persisted with identifiers and computed geometry."""

    id: UUID
    building_id: UUID
    created_at: datetime

    @property
    def area_per_person_m2(self) -> float:
        if self.occupants <= 0:
            return 0.0
        return round(self.floor_area_m2 / self.occupants, 3)


# ---------------------------------------------------------------------------
# Module C — Ventilation
# ---------------------------------------------------------------------------

class VentilationResult(BaseModel):
    """Per-room ventilation screening output."""

    room_id: str
    room_name: str
    floor_area_m2: float
    openable_window_area_m2: float
    opening_ratio_percent: float
    bnbc_min_5_percent: bool
    passes_screening: bool
    room_depth_m: float
    depth_to_height_ratio: float
    cross_ventilation_possible: bool
    single_sided_only: bool
    obstruction_flag: bool
    confidence: ConfidenceLevel
    limitations: list[str]
    recommendations: list[str]
    status: ResultStatus


class VentilationSummary(BaseModel):
    """Project-level ventilation screening summary."""

    rooms_screened: int
    rooms_passing: int
    rooms_below_minimum: int
    needs_review: list[str]
    confidence: ConfidenceLevel


# ---------------------------------------------------------------------------
# Module D — Daylight
# ---------------------------------------------------------------------------

class DaylightResult(BaseModel):
    """Per-room daylight screening output."""

    room_id: str
    room_name: str
    window_area_m2: float
    wall_area_m2: float
    wwr_percent: float
    bnbc_min_10_percent: bool
    effective_glazing_with_obstruction_percent: float
    glazing_vt: float
    overhang_shading: bool
    daylight_potential: str
    confidence: ConfidenceLevel
    limitations: list[str]
    recommendations: list[str]
    status: ResultStatus


class DaylightSummary(BaseModel):
    rooms_screened: int
    rooms_above_minimum: int
    rooms_below_minimum: int
    confidence: ConfidenceLevel


# ---------------------------------------------------------------------------
# Module E — Energy
# ---------------------------------------------------------------------------

class EnergyAssumptions(BaseModel):
    """Explicit assumptions used by the preliminary energy estimator."""

    ac_cop: float = Field(ge=1.5, le=8.0, description="AC coefficient of performance")
    cooling_hours_per_year: float = Field(default=1800.0, ge=0, le=8760)
    lighting_density_w_m2: float = Field(default=7.0, ge=0, le=50, description="W/m²")
    lighting_hours_per_year: float = Field(default=2500.0, ge=0, le=8760)
    equipment_density_w_m2: float = Field(default=5.0, ge=0, le=100, description="W/m²")
    equipment_hours_per_year: float = Field(default=2500.0, ge=0, le=8760)
    ac_capacity_w_m2: float = Field(default=60.0, ge=0, le=500, description="W/m² cooling capacity")


class EnergyBreakdown(BaseModel):
    cooling_kwh: float
    lighting_kwh: float
    equipment_kwh: float


class EnergyResult(BaseModel):
    mode: str = Field(default="preliminary")
    total_electricity_kwh_per_year: float
    energy_performance_index_kwh_m2: float
    breakdown: EnergyBreakdown
    assumptions: EnergyAssumptions
    confidence: ConfidenceLevel
    limitations: list[str]
    status: ResultStatus


# ---------------------------------------------------------------------------
# Module F — Carbon
# ---------------------------------------------------------------------------

class CarbonResult(BaseModel):
    electricity_kwh_per_year: float
    emission_factor_kg_co2_per_kwh: float
    emission_factor_source: str
    emission_factor_year: int
    emission_scope: str
    operational_emissions_kg_co2e_per_year: float
    operational_emissions_t_co2e_per_year: float
    embodied_carbon: Optional[float] = Field(default=None, description="null until verified EPDs exist")
    confidence: ConfidenceLevel
    limitations: list[str]
    status: ResultStatus


# ---------------------------------------------------------------------------
# Module G — Density
# ---------------------------------------------------------------------------

class DensityResult(BaseModel):
    far: Optional[float]
    ground_coverage_percent: Optional[float]
    open_space_percent: Optional[float]
    mandatory_open_space_percent: Optional[float]
    permeable_area_percent: Optional[float]
    rajuk_zone: Optional[str]
    rajuk_dap_far_limit: Optional[float]
    rajuk_dap_coverage_limit: Optional[float]
    far_compliant: Optional[bool] = Field(default=None, description="Computed metric, NOT a compliance claim")
    coverage_compliant: Optional[bool] = None
    open_space_compliant: Optional[bool] = None
    confidence: ConfidenceLevel
    limitations: list[str]
    status: ResultStatus


# ---------------------------------------------------------------------------
# Module H — Structural Screening
# ---------------------------------------------------------------------------

class StructuralFlag(BaseModel):
    flag_id: str
    description: str
    severity: str  # "Review", "High", "Critical"


class StructuralResult(BaseModel):
    missing_information: list[str]
    flags: list[StructuralFlag]
    review_required: bool
    disclaimer: str
    confidence: ConfidenceLevel
    status: ResultStatus


# ---------------------------------------------------------------------------
# Module I — Optimization
# ---------------------------------------------------------------------------

class AlternativeCase(BaseModel):
    name: str
    changes: dict[str, object]
    metric_name: str
    metric_value: float
    difference: float
    percent_difference: float
    confidence: ConfidenceLevel


class OptimizationResult(BaseModel):
    baseline_module: str
    baseline_metric_name: str
    baseline_metric_value: float
    alternatives: list[AlternativeCase]
    method: str
    limitations: list[str]


# ---------------------------------------------------------------------------
# Calculation Result envelope
# ---------------------------------------------------------------------------

class CalculationEnvelope(BaseModel):
    """Full response wrapping every module result with provenance metadata."""

    project_id: str
    calculated_at: datetime
    modules: dict[str, object]
    source_references: list[str]
    overall_confidence: ConfidenceLevel
    disclaimer: str