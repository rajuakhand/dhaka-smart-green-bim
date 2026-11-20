# Detailed MVP Scope: DhakaSmart Urban Density & Green BIM

## Phase 1 — MVP (Minimum Viable Product) — Target: 4 months

### 1.1 Core Modules (Must Ship)

| Module | Key Inputs | Key Outputs | Tech Stack |
|--------|-----------|-------------|------------|
| **A — Building Setup** | Project name, building name, city (Dhaka default), neighborhood coords, building type (residential/mixed-use), number of floors, floor-to-floor height, floor area, orientation (compass degree), construction year (optional), structural system (optional), building geometry (polygon/footprint), adjacent building info (optional) | Project dashboard link, validated inputs summary, source references | FastAPI + PostgreSQL |
| **B — Room and Space Analyzer** | Per room: name, type, length, width, height, floor area, volume, occupants, occupancy schedule, window area, effective openable area, room orientation, adjacent rooms, exterior walls | Per-room: floor area, volume, area/person, occupancy indicators, geometry validation, code checks (BNBC Ch 2) | Python Pydantic models |
| **C — Ventilation Screening** | Openable window area, opening position (single/cross), room depth, adjacent building obstruction (binary input or height offset) | Preliminary ventilation indicators (opening ratio 1-5 scale), potential bottlenecks, missing info, recommendations | Deterministic formulas from BNBC Sec 2.14.6.1 |
| **D — Daylight Screening** | Room dimensions, window geometry, glazing properties (clear/ tinted, VT ratio), external obstruction (height/distance), shading (overhang/fin), sky conditions (clear/ partly cloudy/ overcast) | Daylight screening indicators (DF estimate with confidence level), potential limitations, recommendations | BNBC Sec 2.14.6.1: 10% glazing minimum |
| **E — Energy Estimator** | Cooling-related energy (AC runtime, COP), lighting energy (W/m² × hrs), equipment energy (W/m² × hrs), occupancy assumptions, operating schedules, AC efficiency (EER/COP), envelope properties (U-value, insulation), weather data (EPW) | Two modes: 1) Preliminary energy estimate (kWh/m²/yr), 2) Simulation status (not evaluated in MVP) | Formula: Σ(end-use × hours × power); Use EPW for heating/cooling degree days |
| **F — Carbon Calculator** | Electricity consumption (kWh from Module E), applicable emission factor, emission factor source, data year, emission boundary | Operational electricity emissions = electricity consumption × electricity emission factor; clearly distinguished from embodied carbon | Formula per project principle: Elec × EF; EF = 0.696 kg CO₂e/kWh (Ember 2025) with source |
| **G — Density and Urban Context** | Building footprint, floor area, number of floors, site area, occupancy, surrounding building heights, distances | FAR, ground coverage %, open space %, adjacent building obstruction screening, urban density metrics | FAR = Total Floor Area / Plot Area; Coverage = Footprint / Plot Area |
| **H — Structural Risk Screening** | Structural system, number of floors, building dimensions, column grid, material strength, foundation info, soil info, seismic info, wind exposure, known alterations | Missing information display, potential review flags, reminder: "Requires qualified professional review" | Collect info; display flags; NO structural safety claims |
| **I — Design Optimization** | Baseline vs alternative comparison (window dims, placement, orientation, shading, glazing, wall material, roof properties, ventilation config) | Baseline result, alternative result, difference, % difference, calc method, data confidence, simulation status | Same baseline assumptions for comparison; display all fields per project spec |

### 1.2 Core Features (Must Ship)

- ✅ Building information form with validation
- ✅ Room-wise geometry input (per-room form)
- ✅ Occupancy input (per room, not one universal limit)
- ✅ Window and opening information
- ✅ Building orientation (compass degree input)
- ✅ Basic material input (concrete, brick, insulation — with source reference)
- ✅ Rule-based space analysis (per-module formulas)
- ✅ Preliminary natural ventilation screening
- ✅ Preliminary daylight screening
- ✅ Simplified energy estimation (preliminary mode only)
- ✅ Carbon estimation using traceable emission factor (0.696 kg CO₂e/kWh with source)
- ✅ Design recommendations (derived from screening results)
- ✅ Before/after design comparison (Module I)
- ✅ Analysis summary dashboard
- ✅ Exportable report (PDF/CSV)
- ✅ Data source and assumptions disclosure

### 1.3 Required Pages (17 pages per project spec)

1. Landing page
2. Dashboard
3. Create project
4. Building setup (Module A)
5. Room editor (Module B)
6. Floor plan (visualization)
7. Data sources (with provenance table)
8. Analysis overview
9. Ventilation analysis (Module C)
10. Daylight analysis (Module D)
11. Energy analysis (Module E — preliminary mode only)
12. Carbon analysis (Module F)
13. Density analysis (Module G)
14. Optimization comparison (Module I)
15. Project settings
16. Report export
17. Documentation / methodology

### 1.4 UI Requirements (per project spec)

- ✅ Lightweight, responsive, accessible
- ✅ Engineering-oriented, easy to understand
- ✅ Suitable for low-bandwidth use
- ✅ Desktop and tablet
- ✅ Consistent, not excessively decorative
- ✅ Clear status indicators: Verified / Estimated / Simulated / Not evaluated / Insufficient data / Needs professional review
- ✅ NO green/red pass/fail when analysis not performed

### 1.5 Report Requirements (per project spec)

- ✅ Project details
- ✅ Building details
- ✅ Room details
- ✅ Input summary
- ✅ Data sources
- ✅ Assumptions
- ✅ Rule references
- ✅ Analysis methods
- ✅ Results
- ✅ Recommendations
- ✅ Before/after comparison
- ✅ Uncertainty
- ✅ Limitations
- ✅ Missing information
- ✅ Validation status
- ✅ Professional review warnings
- ✅ Every report identifies analysis as "preliminary" when appropriate

### 1.6 MVP Exclusions (What's NOT in MVP)

| Excluded Feature | Reason | Target Phase |
|-----------------|--------|--------------|
| Weather-based / hourly energy simulation | Requires EnergyPlus integration; input model unstable | Phase 2 |
| Advanced daylight analysis (sDA, ASE) | Requires Radiance simulation | Phase 2 |
| Hourly cooling load calculations | Requires EnergyPlus | Phase 2 |
| BIM IFC upload/extraction | Phase 3 | Phase 3 |
| Sensitivity analysis | Phase 2+ | Phase 2 |
| Design optimization with parametric sweep | Requires stable baseline | Phase 2+ |
| Surrounding building obstruction CFD | Overkill for MVP; use angle screening | Phase 2 |
| Embodied carbon calculation | No verified Bangladesh EPDs | Phase 2 (with Indian factors, flagged) |
| Market-based emission factors | User choice not justified for compliance | Phase 2 |
| CFD integration | Not justified for MVP scale | Phase 3 only if justified |
| Full RAJUK compliance checking | Cannot verify without GIS | Phase 2 with zone lookup |

### 1.7 MVP Data Dictionary (Core Fields Only)

| Field | Module | Type | Constraints | Source |
|-------|--------|------|-------------|--------|
| project_name | A | string | required | user |
| building_name | A | string | optional | user |
| city | A | string | default: "Dhaka" | user / lookup |
| building_type | A | enum [residential, mixed-use, office, commercial, industrial, institutional] | required | user |
| num_floors | A | integer | min: 1, max: 50 (MVP) | user |
| floor_to_floor_height | A | number(m) | min: 2, max: 6 | user |
| floor_area | A | number(m²) | required, > 0 | user |
| orientation_deg | A | number(0-360) | required | user |
| construction_year | A | integer | optional, min: 1900, max: 2026 | user |
| structural_system | A | enum [frame, shear-wall, moment-resist, masonry, load-brick] | optional | user |
| plot_area | G | number(m²) | required, > 0 | user / survey |
| building_footprint | G | polygon/area(m²) | required, > 0 | user input or footprint extraction |
| num_occupants | B | integer | min: 1 | user |
| room_name | B | string | required | user |
| room_type | B | enum [residential, office, classroom, hospital, retail, storage, laboratory, assembly, other] | required | user |
| room_length | B | number(m) | min: 1, max: 50 | user |
| room_width | B | number(m) | min: 1, max: 50 | user |
| room_height | B | number(m) | min: 2, max: 15 | user |
| window_area | B | number(m²) | min: 0 | user |
| openable_window_area | B | number(m²) | min: 0, ≤ window_area | user |
| room_occupants | B | integer | min: 1, max: 100 | user |
| occupancy_schedule | B | enum [daytime, evening, 24hr, custom] | optional | user |
| glazing_type | D | enum [clear, tinted, double_low_e, other] | optional | user / assumption |
| external_obstruction_height | D | number(m) | min: 0 | user input or 0 |
| shading_type | D | enum [overhang, fin, none, both] | optional | user |
| ac_cop | E | number | min: 1.5, max: 8.0 | user / manufacturer |
| ac_runtime_hrs | E | number | min: 0, max: 24 | user assumption or EPW-derived |
| lighting_density | E | W/m² | min: 1, max: 30 (typ 5-10) | user / BNBC default |
| equipment_density | E | W/m² | min: 1, max: 50 | user / assumption |
| electricity_consumption | F | kWh/yr | calculated from Module E | calculated |
| emission_factor_source | F | enum [DoE-GEF, Ember-OWID, User-supplied] | required | selected |
| grid_emission_factor | F | kg CO₂e/kWh | calculated from source | from selected source |
| far | G | number | min: 0.1, max: 20 (DAP range) | calculated: total floor area / plot area |
| ground_coverage | G | % | min: 0, max: 75 (RAJUK DAP Table 3) | calculated: footprint / plot area |
| open_space | G | % | min: 0, max: 60 (RAJUK DAP 1.8.3-1.8.4) | calculated: (plot - footprint) / plot |

### 1.8 MVP Development Phases (Iterative)

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1A | 6 weeks | Project skeleton, data models, API, DB schema, validation, unit tests (calc + geometry) |
| Phase 1B | 6 weeks | Frontend (17 pages), building form, room form, basic visualization, report export |
| Phase 1C | 4 weeks | Calculation engine (all modules A-I), integration, dashboard, before/after comparison |
| Phase 1D | 2 weeks | Testing suite (pytest), data validation, regression tests, security review |
| Phase 1E | 2 weeks | Documentation, deployment config (Docker Compose), user guide draft |

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*