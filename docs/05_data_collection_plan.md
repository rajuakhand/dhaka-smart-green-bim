# Data Collection Plan for Bangladesh

## Phase 1 (MVP) — Core Data Required

| Data Category | Specific Data | Source | Frequency | Status | Collection Method |
|---------------|---------------|--------|-----------|--------|-------------------|
| **Climate** | Dhaka EPW (hourly T, RH, wind, solar, precip), design day (summer/winter) | EnergyPlus / Climate.OneBuilding.org / NASA POWER | Single year (TMYx) | ✅ Obtained | Download via EnergyPlus library; verify with BMD 1991-2020 |
| **Grid Emission Factor** | kg CO₂e/kWh per year (location-based, generation-based) | DoE GEF letter (0.61-0.62 tCO₂/MWh, 2019-22), Ember/OWID (0.696 kg/kWh, 2025) | Annual | ✅ Obtained | Store both; default + user-selectable |
| **Building Energy Baseline** | EPI (kWh/m²/yr) for residential buildings (residential, commercial, institutional) | World Bank BEEER survey (42-54 kWh/m²/yr), SREDA, IEA | Study-based | ⚠️ Partial | Use World Bank survey as range; flag |
| **Occupancy Limits** | Per occupancy type: minimum area/person for residential, etc. | BNBC 2020 Part 3 Ch 2 | Code-based | ✅ Obtained | Extract from BNBC text |
| **Ventilation Minimums** | Opening area per floor area (5%), glazing area (10%) | BNBC 2020 Sec 2.14.6.1 | Code-based | ✅ Obtained | Extract from BNBC text |
| **Occupancy Schedule Reference** | Standard schedules (day, night, commercial) | SREDA / ASHRAE / EN 16798 | Standard-based | ⚠️ Partial | Use EN 16798 / ASHRAE standard defaults |
| **Cooling COP Benchmark** | Average COP for split AC in Bangladesh | SREDA AC Energy Efficiency Benchmark 2021 | Market-based | ⚠️ Partial | Use SREDA benchmark EER/COP values; flag |

## Phase 2 (Advanced) — Additional Data Required

| Data Category | Specific Data | Source | Status |
|---------------|---------------|--------|--------|
| **Monthly Hourly Energy Simulation** | Hourly electricity demand, cooling/heating load | EnergyPlus + Dhaka EPW + validated IDF | ⏳ Planned |
| **SDA / ASE Daylight** | Daylight Autonomy / Annual Solar Exposure | Radiance + Dhaka EPW | ⏳ Planned |
| **Embodied Carbon** | Bangladesh EPDs for concrete, brick, steel, timber, insulation | Green Building Council Bangladesh / ICMD | ⏳ Planned (fallback: ICMD with flag) |
| **Material Property Database** | U-values, thermal mass, conductivity per material | BNBC / manufacturer data / local labs | ⏳ Planned |
| **Urban Context Data** | Surrounding building heights (GIS), building footprints (OSM) | OSM / Landsat / RAJUK GIS | ⏳ Planned |
| **SREDA Cooling Load** | City-level cooling energy demand | SREDA National Cooling Plan, BEEER | ⏳ Planned |

## Phase 3 (BIM) — Additional Data Required

| Data Category | Specific Data | Source | Status |
|---------------|---------------|--------|--------|
| **IFC Files** | Architectural, structural, MEP models | User upload | ⏳ Planned |
| **BIM Geometry Extraction** | Wall/roof/floor/door/window elements | IfcOpenShell | ⏳ Planned |
| **IFC-to-Analysis Model** | Normalized room/space data | Custom converter | ⏳ Planned |

## Data Collection Schedule

| Quarter | Activity | Deliverable |
|---------|----------|-------------|
| Q1 2026 | Data acquisition + source registry | 20+ sources registered, verification statuses set |
| Q2 2026 | EPW + emission factors + climate JSON cache | Cached climate data, emission factor records |
| Q3 2026 | Baseline studies integration | World Bank survey data + occupancy/ventilation rules |
| Q4 2026 | Data validation suite | Completeness checks, unit checks, anomaly flags |

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*