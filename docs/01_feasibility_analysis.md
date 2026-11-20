# Project Feasibility Analysis: DhakaSmart Urban Density & Green BIM

## Executive Summary
This analysis evaluates the technical, regulatory, and data feasibility of building a Bangladesh-specific building performance platform focused on Dhaka's dense urban context.

---

## 1. Technical Feasibility

### 1.1 Core Calculations (Deterministic, MVP-Ready)
| Calculation | Formula | Data Required | Verification Status |
|-------------|---------|---------------|---------------------|
| Floor Area Ratio (FAR) | Total Floor Area / Plot Area | Plot area, floor areas, number of floors | ✅ BNBC 2020, RAJUK DAP rules |
| Ground Coverage | Building Footprint / Plot Area | Building footprint, plot area | ✅ RAJUK DAP Table 3 |
| Open Space Ratio | (Plot Area - Building Footprint) / Plot Area | Plot area, building footprint | ✅ RAJUK DAP 1.8.3-1.8.4 |
| Window-to-Wall Ratio (WWR) | Window Area / Exterior Wall Area | Window dimensions, wall dimensions | ✅ BNBC 2020 Part 3 Ch 1 |
| Ventilation Opening Ratio | Openable Window Area / Floor Area | Window dimensions, opening type, floor area | ✅ BNBC 2020 Sec 2.14.6.1 |
| Daylight Window Ratio | Glazed Area / Floor Area | Window glazing area, floor area | ✅ BNBC 2020 Sec 2.14.6.1 |
| Occupancy Density | Floor Area / Occupant Count | Room area, occupant count | ✅ BNBC 2020 occupancy classification |
| Electricity Consumption Estimate | Σ(End-use × Hours × Power) | Equipment schedules, occupancy, AC COP | ⚠️ Partially verified (SREDA surveys) |
| Operational Carbon | Electricity (kWh) × Grid Emission Factor (kg CO₂e/kWh) | Electricity estimate, emission factor | ✅ Verified: 0.696 kg CO₂e/kWh (Ember 2025) / 0.61-0.62 tCO₂/MWh (DoE 2019-22) |

### 1.2 Simulation Integration (Phase 2+)
| Engine | Input Format | Status for Bangladesh |
|--------|--------------|----------------------|
| EnergyPlus | IDF/EPJSON + EPW | ✅ EPW available for Dhaka (SWERA 419230, TMYx from climate.onebuilding.org) |
| Radiance | RAD + EPW | ✅ EPW available |
| OpenFOAM (CFD) | Case files | ❌ Not justified for MVP |

---

## 2. Regulatory Feasibility

### 2.1 Verified Applicable Codes & Standards
| Document | Status | Coverage for MVP |
|----------|--------|------------------|
| **BNBC 2020** (Gazette 11 Feb 2021) | ✅ In force | Occupancy (Ch 2), Ventilation/Daylight (Sec 2.14.6), Energy Efficiency (Ch 4), Plot rules (Ch 1) |
| **RAJUK DAP 2022-2035** (Gazette 24 Aug 2022) | ✅ In force | FAR by zone, ground coverage by plot size, height limits, open space |
| **Dhaka Metropolitan Building Rules 2025** (Draft, approved Oct 2025) | ⚠️ Pending gazette | Stricter deviation control, STP for >5 katha, green building incentives |
| **SREDA BEEER v2** (Jan 2023) | ✅ Voluntary | Rating framework, minimum 10,000 sqft, baseline references |
| **Energy Efficiency & Conservation Rules 2016** | ✅ In force | Designated consumers, energy audits |
| **Building Construction Act 1952 (Amended)** | ✅ In force | Legal basis for BNBC |

### 2.2 Gap Analysis
| Area | Code Coverage | Data Gap | Mitigation |
|------|---------------|----------|------------|
| Residential cooling load baseline | BNBC Ch 4 references but no explicit values | No official EPI baseline for residential | Use World Bank survey: 42-54 kWh/m²/yr |
| Embodied carbon factors | Not in BNBC | No Bangladesh-specific EPD database | Use India ICMD (Chaudhary & Akhtar 2023) with verification flag |
| Urban wind environment | Not quantified | No city-scale CFD | Use EPW wind data + obstruction screening (MVP) |

---

## 3. Data Feasibility

### 3.1 Verified Data Sources (Prioritized per Project Governance)

| Priority | Source | Data Type | Access | Verification |
|----------|--------|-----------|--------|--------------|
| 1 | BNBC 2020 Gazette | Regulatory requirements | Public PDF | ✅ Official |
| 1 | RAJUK DAP Gazette + Maps | FAR, coverage, zoning | Public PDF/Web | ✅ Official |
| 1 | DoE Grid Emission Factor 2019-22 | 0.61-0.62 tCO₂/MWh | Official letter | ✅ Government |
| 1 | Ember/OWID Electricity Carbon Intensity | 0.696 kg CO₂e/kWh (2025) | CC BY 4.0 | ✅ Independent |
| 1 | Climate.OneBuilding.org | Dhaka EPW (TMYx) | Free download | ✅ Derived from NASA POWER |
| 1 | NASA POWER API | Hourly solar, met, 0.5° grid | Free API | ✅ Satellite-derived |
| 2 | SREDA BEEER Guideline | Rating criteria, baselines | Public PDF | ✅ Official |
| 2 | World Bank BEEER Survey (2023) | 277 kWh/m²/yr (mixed), 42 kWh/m²/yr (residential) | Public PDF | ✅ Measured sample |
| 2 | BMD Solar Radiation (Angstrom-Prescott) | 5 stations, 2017 measured | Journal paper | ⚠️ Limited stations |
| 3 | Chaudhary & Akhtar 2023 (ACS Environ. Au) | 78 material GWP factors, India | Peer-reviewed | ✅ Verified, marked geography |
| 3 | SREDA NSHD Solar Station (Dhaka) | Measured GHI, Motijheel | Web portal | ⚠️ Single station |

### 3.2 Critical Data Gaps
| Gap | Impact | Workaround |
|-----|--------|------------|
| No Bangladesh-specific construction EPDs | Embodied carbon estimates unverified | Use Indian ICMD factors with `Unverified-Bangladesh` flag; require user confirmation |
| No official residential EPI baseline | Energy benchmarking uncertain | Use World Bank survey (42 kWh/m²/yr) + SREDA 28.8% savings potential as range |
| No city-scale urban wind model | Cross-ventilation screening approximate | EPW hourly wind + obstruction angle screening |
| RAJUK DAP zone FAR requires plot-level lookup | Automation needs GIS integration | MVP: manual FAR input with zone reference; Phase 2: GeoJSON overlay |

---

## 4. Resource Feasibility

### 4.1 Team Skills Required vs Available
| Role | Required | Available (This Project) |
|------|----------|--------------------------|
| Software Architect | System design, API, DB | ✅ |
| Full-Stack Developer | React/Next.js, FastAPI, Docker | ✅ |
| Building Performance Engineer | Ventilation, daylight, energy calcs | ⚠️ Must implement from verified formulas |
| BIM Engineer | IfcOpenShell, IFC parsing | ⚠️ Phase 3 |
| Energy Analyst | EnergyPlus, baseline modeling | ⚠️ Phase 2 |
| Climate Data Scientist | EPW, NASA POWER, statistical analysis | ✅ Can use pvlib, epw libraries |
| QA/Test Engineer | pytest, calculation validation | ✅ |
| Cybersecurity Engineer | Input sanitization, file upload safety | ✅ |

### 4.2 Infrastructure
| Component | MVP | Phase 2+ |
|-----------|-----|----------|
| Compute | Local Docker Compose | Cloud (GPU for simulation) |
| Storage | Local PostgreSQL + file storage | Object storage (S3-compatible) |
| CI/CD | GitHub Actions | GitHub Actions + self-hosted runners |

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| BNBC 2020 full text not machine-readable | High | Medium | Extract key tables manually; maintain source registry with clause refs |
| RAJUK DAP zone data not in GIS format | High | Medium | MVP: manual zone selection with FAR table; Phase 2: acquire shapefiles |
| Electricity emission factor dispute (0.61 vs 0.696) | Medium | High | Store both with source; user selects; default to DoE for compliance, Ember for international reporting |
| IFC geometry extraction failures | Medium | High (Phase 3) | Validate with IfcOpenShell test suite; geometry repair pipeline |
| User over-relies on preliminary results | High | High | Mandatory uncertainty/confidence display; professional review warnings |

---

## 6. Go/No-Go Decision

**GO for MVP** — Core calculations are deterministic, traceable to BNBC 2020 and RAJUK DAP, climate data is available (EPW), electricity emission factors are documented from multiple sources with clear provenance.

**Conditions:**
1. Every calculation must cite its code section or data source
2. No embodied carbon in MVP without verified EPDs
3. All results must show confidence/limitation status
4. Professional review disclaimer on every report

---

## 7. Assumptions Register

| ID | Assumption | Status | Validation Plan |
|----|------------|--------|-----------------|
| A-01 | BNBC 2020 Sec 2.14.6.1 (10% glazing, 5% openable) is the applicable minimum for all occupancies | Verified | Cross-check BNBC 2020 Part 3 Ch 2 occupancy-specific overrides |
| A-02 | Dhaka EPW (SWERA 419230) represents typical year for energy simulation | Verified | Compare TMYx stats with BMD 1991-2020 normals |
| A-03 | Grid emission factor 0.696 kg CO₂e/kWh (Ember 2025) is appropriate for Scope 2 location-based | Partially verified | Document both DoE (0.61-0.62) and Ember; let user choose |
| A-04 | Residential EPI baseline 42 kWh/m²/yr (World Bank survey) is representative | Partially verified | Flag as sample of 30 buildings; sensitivity analysis in reports |
| A-05 | Cross-ventilation potential can be screened from geometry + EPW wind rose | Assumption | Validate against measured ACH studies if available; label "screening only" |

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*