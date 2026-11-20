# Calculation Inventory

## All Deterministic Calculations (MVP Phase 1)

### Module A — Building Setup Calculations
| # | Calculation Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|---------|--------|--------|-------|--------|------------|-----------|
| A1 | Floor Area Validation | Sum(rooms.floor_area) ≈ building.total_floor_area | rooms[] | total_area_m2 | m² | User | High | Valid |
| A2 | Plot Coverage (preliminary) | building_footprint / plot_area × 100 | footprint, plot | coverage_pct | % | RAJUK DAP | Medium | Valid |

### Module B — Room Analyzer Calculations
| # | Calculation Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|---------|--------|--------|-------|--------|------------|-----------|
| B1 | Floor Area | length × width | length, width | area_m2 | m² | Geometry | High | Valid |
| B2 | Volume | floor_area × height | area, height | volume_m3 | m³ | Geometry | High | Valid |
| B3 | Area per Person | floor_area / occupants | area, occupants | area_person_m2 | m²/pers | BNBC | Medium | Valid |
| B4 | Occupancy Indicator | Compare area_person_m2 vs BNBC minimum | area, occupants, bnbc_min | pass/fail | - | BNBC | Medium | Valid |
| B5 | Volume Validation | height > 0; volume > 0 | height | valid | - | Geometry | High | Valid |

### Module C — Ventilation Screening Calculations
| # | Calculation Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|---------|--------|--------|-------|--------|------------|-----------|
| C1 | Opening Ratio | openable_window_area / floor_area × 100 | openable_area, area | ratio_pct | % | BNBC 5% | High | Valid |
| C2 | WWR Screening | window_area / wall_area × 100 | window_area, wall_area | wwr_pct | % | BNBC/n/a | High | Valid |
| C3 | Room Depth Ratio | room_depth / room_height | depth, height | ratio | - | SIA/n/a | Low | Valid (screen only) |
| C4 | Cross-Ventilation Potential | Binary: single vs cross openings feasible by geometry | window positions, depth | possible/not | - | Screening | Low | Valid (screen only) |

### Module D — Daylight Screening Calculations
| # | Calculation Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|---------|--------|--------|-------|--------|------------|-----------|
| D1 | Glazing Ratio | window_area / floor_area × 100 | window_area, area | glazed_pct | % | BNBC 10% | High | Valid |
| D2 | Effective Glazing (obstruction) | window_area × (1 - obstruction_factor) | window_area, obstruction | effective_pct | % | Screen | Low | Valid (screen only) |
| D3 | Overhang Shading | Binary: overhang present or not | shading_type, dimensions | shaded | - | Screen | Low | Valid (screen only) |

### Module E — Energy Estimator (Preliminary) Calculations
| # | Calculation Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|---------|--------|--------|-------|--------|------------|-----------|
| E1 | Cooling Energy | Σ(AC_kW × COP × hours) | ac_cop, runtime_hrs, ac_kw | cooling_kwh | kWh | SREDA/benchmark | Low | Valid (preliminary) |
| E2 | Lighting Energy | Σ(lighting_density × floor_area × hours) | lighting_density, area, hours | lighting_kwh | kWh | BNBC/n/a | Medium | Valid (preliminary) |
| E3 | Equipment Energy | Σ(equipment_density × area × hours) | equipment_density, area, hours | equip_kwh | kWh | Assumption | Low | Valid (preliminary) |
| E4 | Total Electricity | Cooling + Lighting + Equipment (+ other) | components | total_kwh | kWh | Sum | High | Valid |
| E5 | EPI | total_kwh / total_floor_area | total_kwh, area | epi | kWh/m²/yr | Derived | Medium | Valid (preliminary) |

### Module F — Carbon Calculator Calculations
| # | Calculation Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|---------|--------|--------|-------|--------|------------|-----------|
| F1 | Operational Electricity Emissions | electricity_kwh × grid_emission_factor | kwh, factor | emissions_kg_co2e | kg CO₂e/yr | Emission Factor | High | Valid |
| F2 | Operational Emissions (tCO₂e) | electricity_kwh × factor / 1000 | F1 result | t_co2e | t CO₂e/yr | Derived | High | Valid |
| F3 | Carbon Breakdown | Total = Operational; Embodied = null (not computed) | E4 result | breakdown | kg CO₂e | Decision | High | Valid |

### Module G — Density & Urban Context Calculations
| # | Calculation Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|---------|--------|--------|-------|--------|------------|-----------|
| G1 | FAR | total_floor_area / plot_area | total_floor_area, plot_area | far | - | BNBC/RAJUK | Medium | Valid |
| G2 | Ground Coverage | building_footprint / plot_area × 100 | footprint, plot | coverage_pct | % | RAJUK DAP | Medium | Valid |
| G3 | Open Space | (plot_area - footprint) / plot_area × 100 | plot, footprint | open_space_pct | % | RAJUK DAP | Medium | Valid |
| G4 | Occupancy Density | building_footprint × num_floors / occupants | footprint, floors, occupants | occ_density | pers/m² | BNBC | Medium | Valid |

### Module H — Structural Risk Screening Calculations
| # | Calculation Name | Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|------|---------|--------|--------|-------|--------|------------|-----------|
| H1 | Height Review Flag | Is num_floors > 6? | num_floors | flag | - | BNBC Part 6 | Medium | Valid |
| H2 | Age Review Flag | Is construction_year > 20 yrs? | construction_year | flag | - | BNBC | Low | Valid |

### Module I — Design Optimization Calculations
| # | Calculation Name | Name | Formula | Inputs | Output | Unit | Source | Confidence | Test Type |
|---|-------------------|------|---------|--------|--------|-------|--------|------------|-----------|
| I1 | Alternative Metric | Re-run Module E (or relevant) with changed inputs | changes[] | metric_value | kWh/m²/yr | Same method | Medium | Valid |
| I2 | Delta (Absolute) | alternative_value - baseline_value | values | delta | - | Same method | Medium | Valid |
| I3 | Delta (Percent) | delta / baseline_value × 100 | delta, baseline | pct_change | % | Same method | Medium | Valid |

## Calculation Summary Table (Phase 1)

| Module | Calculation Count | Formulas Implemented | Reference Tests Planned | Status |
|--------|-------------------|----------------------|--------------------------|--------|
| A | 2 | 2 | 4 | ✅ In Progress |
| B | 5 | 5 | 10 | ✅ In Progress |
| C | 4 | 4 | 8 | ✅ In Progress |
| D | 3 | 3 | 6 | ✅ In Progress |
| E | 5 | 5 | 12 | ✅ In Progress |
| F | 3 | 3 | 6 | ✅ In Progress |
| G | 4 | 4 | 8 | ✅ In Progress |
| H | 2 | 2 | 4 | ✅ In Progress |
| I | 3 | 3 | 6 | ✅ In Progress |

## Regression Protection Rules

1. **Never change a calculation without updating reference tests**
2. **All formulas isolated in dedicated module functions** (not embedded in views)
3. **No hard-coded engineering values** — all values from source registry or user input
4. **No silent fallbacks** — missing data → result marked `Insufficient` or `Not evaluated`

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*