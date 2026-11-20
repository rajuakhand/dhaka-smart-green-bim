# Source Verification Plan

## Governance Principles (per Project Non-Negotiable Rules)

1. Never invent code requirements, climate data, material properties, emission factors, or measured data.
2. Every engineering rule must have a traceable source.
3. Every calculation must be deterministic, testable, and documented.
4. AI must never replace engineering calculation logic.
5. Never report simulated values as measured values.
6. Never report estimated values as verified values.
7. Never hide uncertainty or limitations.
8. Never use an unverified rule as a compliance requirement.

## Source Verification Workflow

```
1. IDENTIFY → What rule/data do we need?
2. FIND SOURCE → Document reference, URL, publication date
3. VERIFY → Check source is official, peer-reviewed, or manufacturer
4. EXTRACT → Extract exact clause/table/formula, note section
5. RECORD → Store in source_registry with verification_status
6. CROSS-CHECK → Compare with 2+ sources if available
7. LABEL → Assign confidence level (High/Medium/Low/Insufficient)
```

## Source Register (MVP - Initial)

### Tier 1: Official Government / Regulatory

| ID | Source Name | URL/Reference | Publisher | Type | Coverage | Status | Notes |
|----|-------------|---------------|-----------|------|----------|--------|-------|
| SRC-001 | BNBC 2020 (Bangladesh National Building Code) | http://uru.gov.bd/attachments/documents/166-1618152305-8.1(b) BNBC 2020 implementation... | MoPHW / RAJUK | Regulatory Code | Bangladesh | ✅ Verified (Gazette 11 Feb 2021) | Occupancy Ch 2, Ventilation Sec 2.14.6.1, Energy Ch 4 |
| SRC-002 | RAJUK DAP 2022-2035 | rajuk.gov.bd / masterplan.rajuk.gov.bd | RAJUK / MoPHW | Master Plan | Dhaka (1528 km²) | ✅ Verified (Gazette 24 Aug 2022) | FAR by zone, ground coverage by plot size, height limits |
| SRC-003 | Dhaka Metropolitan Building Construction Rules 2025 (Draft) | MoPHW draft (Oct 2025) | MoPHW | Draft Regulation | Dhaka | ⚠️ Pending Gazette | Stricter deviation, STP >5 katha, green incentives |
| SRC-004 | SREDA BEEER Guideline v2 (Jan 2023) | sreda.gov.bd / Building Energy Efficiency & Environment Rating | SREDA | Rating Standard | Bangladesh | ✅ Verified (Voluntary) | Rating criteria, 10,000 sqft threshold |
| SRC-005 | Energy Efficiency & Conservation Rules 2016 | SREDA | SREDA | Regulation | Bangladesh | ✅ Verified | Designated consumers, energy audits |

### Tier 2: Government Data / Official Statistics

| ID | Source Name | URL/Reference | Publisher | Type | Coverage | Status | Notes |
|----|-------------|---------------|-----------|------|----------|--------|-------|
| SRC-006 | Grid Emission Factor (GEF) for Bangladesh 2019-22 | DOE letter ref. 22.02.0000.063.61.009.23-37, 23 Jan 2025 | DoE / MoCC | Official Emission Factor | Bangladesh | ✅ Verified (0.61-0.62 tCO₂/MWh) | Location-based Scope 2 factor |
| SRC-007 | Grid Emission Factor (GEF) 2013 | DOE letter ref. 20 12/21/07, 19 Aug 2013 | DoE / MoCC | Official Emission Factor | Bangladesh | ✅ Verified (0.67 tCO₂/MWh) | Historical factor |
| SRC-008 | World Bank BEEER Survey (2023) | "Implementation support for BEEER", World Bank P172183 | World Bank | Baseline Study | Bangladesh (30 buildings) | ⚠️ Partial (sample) | EPI: 277 kWh/m²/yr (mixed), 42 kWh/m²/yr (residential) |
| SRC-009 | Bangladesh Climate Action Roadmap for Buildings (2025) | globalabc.org / MOPHW | GlobalABC / UNEP | Roadmap | Bangladesh | ⚠️ Partial | Operational carbon: 29.8 Mt CO₂e (2024), 45.1 by 2030 |
| SRC-010 | BMD Solar Radiation (Angstrom-Prescott, 2023) | server6.bmd.gov.bd / DEW-DROP Vol 9, June 2023 | BMD | Research | 5 stations (incl Dhaka) | ⚠️ Partial (limited) | Solar radiation estimation model |

### Tier 3: Meteorological & Simulation Data

| ID | Source Name | URL/Reference | Publisher | Type | Coverage | Status | Notes |
|----|-------------|---------------|-----------|------|----------|--------|-------|
| SRC-011 | EnergyPlus Weather File (EPW) for Dhaka | energyplus.net/weather (SWERA 419230) | DOE / NREL | Simulation Input | Dhaka (23.66°N, 90.38°E) | ✅ Verified | TMYx, ~8760 hourly records |
| SRC-012 | NASA POWER (hourly solar, met) | power.larc.nasa.gov | NASA | Satellite-derived | Global (0.5° grid) | ✅ Verified | T2M, RH2M, ALLSKY_SFC_SW_DWN, WS2M |
| SRC-013 | SREDA NSHD Solar Station (Dhaka) | nshd.sreda.gov.bd | SREDA | Measured (pyranometer) | Dhaka (Motijheel) | ⚠️ Limited | Single station; 2024-2025 |

### Tier 4: International / Peer-Reviewed / Research

| ID | Source Name | URL/Reference | Publisher | Type | Coverage | Status | Notes |
|----|-------------|---------------|-----------|------|----------|--------|-------|
| SRC-014 | Ember/OWID Electricity Carbon Intensity | github.com/owid/energy-data | Ember / OWID | Dataset (CC BY 4.0) | Bangladesh (annual) | ✅ Verified | 0.696 kg CO₂e/kWh (2025); generation-based, not consumption |
| SRC-015 | Chaudhary & Akhtar 2023 (ICMD factors) | pubs.acs.org/doi/10.1021/acsenvironau.2c00035 | ACS Environ. Au | Peer-reviewed (India) | India (78 materials) | ✅ Verified | Cradle-to-gate GWP; NOT Bangladesh-specific |
| SRC-016 | SREDA AC Energy Efficiency Benchmark 2021 | sreda.gov.bd | SREDA | Market Study | Bangladesh (AC) | ⚠️ Partial | EER/COP averages by AC type |
| SRC-017 | IFC India Construction Materials Database | edgebuildings.com / IFC | IFC | Database | India | ✅ Verified | Embodied carbon factors (cradle-to-gate) |

### Tier 5: Industry / Manufacturer / Local

| ID | Source Name | URL/Reference | Publisher | Type | Coverage | Status | Notes |
|----|-------------|---------------|-----------|------|----------|--------|-------|
| SRC-018 | RSC Technical Guidelines (Bangladesh) | rsc-bd.org / RMG Sustainability Council | RMG Sustainability Council | Industry Standard | Bangladesh (RMG) | ⚠️ Partial | RMG-specific; not for all buildings |
| SRC-019 | HBRI Construction Guidelines | hbri.gov.bd | HBRI | Technical Guideline | Bangladesh | ⚠️ Partial | Construction practices; limited |

## Verification Status Definitions (per Project Spec §7)

| Status | Meaning | Evidence Required |
|--------|---------|-------------------|
| ✅ Verified | Official source, published, verified by project team | Official document + cross-check |
| ⚠️ Partially verified | Source exists but limited scope or incomplete data | Source + scope limitations noted |
| ⏳ Pending verification | Source identified but not yet confirmed | Initial research only |
| ❌ Unavailable | Source could not be found or accessed | Documented gap |
| 📝 User supplied | User-provided data, unverified by project | Label as user input |
| 🟡 Estimated | Derived from assumptions, not measured | Document assumptions |

## Rules for Source Selection (per Project Spec §7 priority)

1. **Highest priority**: Applicable official Bangladesh regulations and standards (BNBC, RAJUK DAP, SREDA)
2. **Second priority**: Bangladesh government datasets (DoE, BMD, SREDA)
3. **Third priority**: Verified meteorological datasets (BMD, NASA POWER, EPW)
4. **Fourth priority**: Peer-reviewed scientific research (Chaudhary & Akhtar, etc.)
5. **Fifth priority**: Manufacturer technical datasheets
6. **Sixth priority**: Verified local measurements (RSC, HBRI)
7. **Seventh priority**: International reference datasets (IEA, World Bank)
8. **Last priority**: Explicitly labeled fallback assumptions (user must acknowledge)

## Source Registry File Structure (CSV Schema)

```csv
source_id,source_type,source_name,source_url,boundary,geography,publisher,date_accessed,version,license,verification_status,notes
```

This CSV will be stored at `data/source_registry.csv` and loaded by the backend.

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*