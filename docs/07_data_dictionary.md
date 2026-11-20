# Data Dictionary

## Core Entity Definitions (MVP)

### Project (Building-Level)

| Field | Type | Constraints | Unit | Description | Module | Source/Validation |
|-------|------|-------------|------|-------------|--------|-------------------|
| id | UUID | PK, auto | - | Unique project identifier | All | System |
| name | string | required, 1-100 chars | - | Project name (e.g., "Dhaka Residential Block A") | A | User |
| building_name | string | optional, 1-100 | - | Building identifier (can be anonymized) | A | User |
| city | string | required, default "Dhaka" | - | City name | A | User/lookup |
| latitude | decimal | optional, -90 to 90 | deg | Geographic latitude | A,G | User/GIS |
| longitude | decimal | optional, -180 to 180 | deg | Geographic longitude | A,G | User/GIS |
| building_type | enum | required | - | Residential, Mixed-use, Office, Commercial, Industrial, Institutional | A | BNBC Ch 2 |
| num_floors | integer | required, 1-50 | - | Number of floors above ground | A | User |
| floor_to_floor_height | decimal | required, 2.0-6.0 | m | Typical floor-to-floor height | A,B | User |
| total_floor_area | decimal | required, >0 | m² | Sum of all floor areas | A,G | User (calculated from rooms) |
| orientation_deg | decimal | required, 0-360 | deg | Building primary orientation (0=N) | A,C,D | User |
| construction_year | integer | optional, 1900-2026 | year | Year of construction (for existing) | A,H | User |
| structural_system | enum | optional | - | Frame, Shear-wall, Moment-resist, Masonry, Load-brick | A,H | User |
| plot_area | decimal | optional, >0 | m² | Total site/plot area | G | User/survey |
| building_footprint | geometry | optional | m² | Building footprint polygon | G | User/GIS |
| created_at | timestamp | auto | - | Record creation time | All | System |
| updated_at | timestamp | auto | - | Last modification time | All | System |

### Room (Space-Level)

| Field | Type | Constraints | Unit | Description | Module | Source/Validation |
|-------|------|-------------|------|-------------|--------|-------------------|
| id | UUID | PK, auto | - | Unique room identifier | B | System |
| project_id | UUID | FK → projects.id | - | Parent project | B | System |
| name | string | required, 1-50 | - | Room name/label | B | User |
| room_type | enum | required | - | Residential, Office, Classroom, Hospital, Retail, Storage, Lab, Assembly, Other | B | BNBC Ch 2 |
| length | decimal | required, 1.0-50.0 | m | Room length | B | User |
| width | decimal | required, 1.0-50.0 | m | Room width | B | User |
| height | decimal | required, 2.0-15.0 | m | Room height (ceiling height) | B | User |
| floor_area | decimal | computed = length × width | m² | Room floor area | B | System (validated) |
| volume | decimal | computed = floor_area × height | m³ | Room volume | B | System |
| window_area | decimal | optional, ≥0, ≤ wall_area | m² | Total window glazing area | B,C,D | User |
| openable_window_area | decimal | optional, ≥0, ≤ window_area | m² | Effective openable area | B,C | User |
| occupants | integer | required, 1-100 | persons | Design occupancy | B | User |
| occupancy_schedule | enum | optional | - | Daytime, Evening, 24hr, Custom | B,E | User |
| orientation_deg | decimal | optional, 0-360 | deg | Room orientation (if different from building) | B,C,D | User |
| glazing_type | enum | optional | - | Clear, Tinted, Double-Low-E, Other | D | User/manufacturer |
| external_obstruction_height | decimal | optional, ≥0 | m | Height of adjacent obstruction | D | User/GIS |
| shading_type | enum | optional | - | None, Overhang, Fin, Both | D | User |
| created_at | timestamp | auto | - | Record creation | All | System |

### Calculation Result (Per Module)

| Field | Type | Constraints | Unit | Description | Module |
|-------|------|-------------|------|-------------|--------|
| id | UUID | PK, auto | - | Result identifier | All |
| project_id | UUID | FK → projects.id | - | Parent project | All |
| module_id | string | required, A-I | - | Module identifier | All |
| version | integer | required, ≥1 | - | Calculation version | All |
| input_snapshot | JSONB | required | - | Inputs used for this calculation | All |
| result | JSONB | required | varies | Calculated outputs (see module schemas) | All |
| confidence | enum | required | - | High, Medium, Low, Insufficient | All |
| limitations | JSONB (text[]) | required | - | Known limitations | All |
| source_references | JSONB (text[]) | required | - | Source IDs used (SRC-XXX) | All |
| calculated_at | timestamp | auto | - | Calculation timestamp | All |

## Module Output Schemas (JSONB result structure)

### Module A — Building Setup
```json
{
  "validated": true,
  "errors": [],
  "warnings": [],
  "plot_validation": {
    "footprint_fits_plot": true,
    "footprint_area_m2": 500,
    "plot_area_m2": 1000,
    "coverage_percent": 50
  }
}
```

### Module B — Room Analyzer
```json
{
  "rooms": [
    {
      "room_id": "uuid",
      "floor_area_m2": 20,
      "volume_m3": 60,
      "area_per_person_m2": 20,
      "occupancy_type": "residential",
      "bnbc_compliance": {
        "min_area_per_person_m2": 9.3,
        "passes": true
      },
      "geometry_warnings": []
    }
  ],
  "summary": {
    "total_rooms": 12,
    "total_floor_area_m2": 240,
    "total_volume_m3": 720,
    "total_occupants": 48
  }
}
```

### Module C — Ventilation Screening
```json
{
  "rooms": [
    {
      "room_id": "uuid",
      "opening_ratio_percent": 4.5,
      "bnbb_min_5_percent": false,
      "cross_ventilation_possible": true,
      "single_sided_only": false,
      "room_depth_m": 5.0,
      "depth_to_height_ratio": 2.0,
      "obstruction_flag": false,
      "confidence": "Medium",
      "limitations": ["Screening only; not ACH calculation"]
    }
  ],
  "summary": {
    "rooms_with_cross_vent": 8,
    "rooms_below_min_opening": 3,
    "needs_review": ["room-2", "room-5"]
  }
}
```

### Module D — Daylight Screening
```json
{
  "rooms": [
    {
      "room_id": "uuid",
      "wwr_percent": 12.5,
      "bnbb_min_10_percent": true,
      "effective_wwr_with_obstruction": 10.2,
      "glazing_vt": 0.85,
      "overhang_shading": true,
      "daylight_potential": "Adequate",
      "confidence": "Low",
      "limitations": ["No sDA/ASE simulation; WWR screening only"]
    }
  ]
}
```

### Module E — Energy Estimator (Preliminary)
```json
{
  "mode": "preliminary",
  "total_electricity_kwh_per_yr": 125000,
  "energy_performance_index_kwh_per_m2": 52.1,
  "breakdown": {
    "cooling_kwh": 68000,
    "lighting_kwh": 25000,
    "equipment_kwh": 32000
  },
  "assumptions": {
    "ac_cop": 3.1,
    "cooling_hours_yr": 1800,
    "lighting_density_w_m2": 7,
    "equipment_density_w_m2": 5,
    "occupancy_hours_yr": 3000
  },
  "confidence": "Medium",
  "limitations": ["Preliminary estimate; no simulation"]
}
```

### Module F — Carbon Calculator
```json
{
  "electricity_kwh_per_yr": 125000,
  "emission_factor_kg_co2_per_kwh": 0.696,
  "emission_factor_source": "Ember/OWID 2025",
  "emission_factor_year": 2025,
  "operational_emissions_kg_co2e_per_yr": 87000,
  "operational_emissions_t_co2e_per_yr": 87.0,
  "scope": "Location-based (Scope 2)",
  "embodied_carbon": null,
  "confidence": "High",
  "limitations": ["Only operational electricity; no embodied, transport, EOL"]
}
```

### Module G — Density & Urban Context
```json
{
  "far": 2.4,
  "ground_coverage_percent": 50,
  "open_space_percent": 50,
  "mandatory_open_space_percent": 35,
  "permeable_area_percent": 20,
  "rajuk_dap_zone": "Mirpur",
  "rajuk_dap_far_limit": 3.4,
  "rajuk_dap_coverage_limit": 65,
  "surrounding_obstruction": {
    "max_height_m": 18,
    "min_distance_m": 4.5,
    "obstruction_angle_deg": 25
  },
  "compliance": {
    "far_compliant": true,
    "coverage_compliant": true,
    "open_space_compliant": true
  },
  "confidence": "Medium",
  "limitations": ["Zone FAR from manual lookup; not GIS-verified"]
}
```

### Module H — Structural Risk Screening
```json
{
  "missing_information": [
    "Structural drawings not provided",
    "Material strength (concrete grade) not specified",
    "Foundation type unknown",
    "Soil investigation report not available",
    "Seismic zone verification needed"
  ],
  "flags": [
    "Building > 6 floors: requires seismic design per BNBC Part 6",
    "Age > 20 years: potential material degradation",
    "Adjacent excavation: potential foundation impact"
  ],
  "review_required": true,
  "disclaimer": "This is NOT a structural assessment. Requires qualified structural engineer."
}
```

### Module I — Design Optimization Comparison
```json
{
  "baseline": {
    "module": "E",
    "metric": "epi_kwh_per_m2",
    "value": 52.1
  },
  "alternatives": [
    {
      "name": "Improved glazing + overhangs",
      "changes": {"glazing_type": "double_low_e", "shading_type": "both"},
      "value": 44.3,
      "difference": -7.8,
      "percent_difference": -15.0,
      "confidence": "Medium"
    },
    {
      "name": "Higher COP AC (3.5→4.0)",
      "changes": {"ac_cop": 4.0},
      "value": 48.2,
      "difference": -3.9,
      "percent_difference": -7.5,
      "confidence": "Medium"
    }
  ],
  "method": "Preliminary energy estimator",
  "limitations": ["Same baseline assumptions; not simulation"]
}
```

## Reference Data Tables (Seeded)

### emission_factors
| source_id | year | factor_kg_co2_per_kwh | scope | is_default | verified | source_url |
|-----------|------|----------------------|-------|------------|----------|------------|
| DoE-GEF | 2022 | 0.62 | location-based | true | true | DOE letter 22.02.0000.063.61.009.23-37 |
| Ember-OWID | 2025 | 0.696 | generation-based | false | true | github.com/owid/energy-data |

### bnbc_rules
| rule_id | section | description | formula | required_inputs | applicability | verified |
|---------|---------|-------------|---------|-----------------|---------------|----------|
| BNBC-2020-2.14.6.1 | 2.14.6.1 | Natural light: min 10% glazed area of floor area | glazed_area / floor_area ≥ 0.10 | window_area, floor_area | All occupied rooms | true |
| BNBC-2020-2.14.6.1b | 2.14.6.1 | Natural ventilation: min 5% openable area of floor area | openable_area / floor_area ≥ 0.05 | openable_window_area, floor_area | All occupied rooms | true |

### weather_stations
| wmo_code | city | latitude | longitude | elevation | epw_source | epw_path | tm_years |
|----------|------|----------|-----------|-----------|------------|----------|----------|
| 419230 | Dhaka | 23.728 | 90.407 | 6 | EnergyPlus/SWERA | data/epw/Dhaka_419230.epw | [2007-2021] |

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*