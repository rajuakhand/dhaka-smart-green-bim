# Risk Register

## Risk Categories

| Category | Description |
|----------|-------------|
| R-DATA | Data quality, availability, verification |
| R-REG | Regulatory interpretation, compliance claims |
| R-TECH | Technical implementation, architecture, scalability |
| R-USER | User expectations, misuse of preliminary results |
| R-SEC | Security, privacy, file upload safety |
| R-PROJ | Project management, timeline, scope creep |

## Identified Risks

| ID | Category | Risk Description | Likelihood | Impact | Risk Score | Mitigation | Owner | Status |
|----|----------|------------------|------------|--------|------------|------------|-------|--------|
| RSK-001 | R-DATA | **No verified Bangladesh construction EPDs** — embodied carbon cannot be calculated reliably | High | High | 🔴 Critical | Exclude embodied carbon from MVP; Phase 2: use ICMD with explicit `Unverified-Bangladesh` flag; require user acknowledgment | Data Engineer | Accepted |
| RSK-002 | R-DATA | **Grid emission factor discrepancy** — DoE GEF (0.61-0.62) vs Ember (0.696) — users may challenge | Medium | High | 🔴 Critical | Store both with source metadata; default to DoE for compliance, Ember for international reporting; user selects | Data Engineer | Accepted |
| RSK-003 | R-DATA | **EPW representativeness** — Single EPW (SWERA 419230) may not reflect microclimate | Medium | Medium | 🟡 High | Document EPW source; provide NASA POWER as alternative; sensitivity analysis in Phase 2 | Climate Engineer | Accepted |
| RSK-004 | R-REG | **RAJUK DAP zone data not in machine-readable format** — manual lookup errors | High | Medium | 🔴 Critical | MVP: manual FAR/coverage input with zone reference table; Phase 2: acquire GeoJSON | Backend Engineer | Planned |
| RSK-005 | R-REG | **BNBC 2020 text extraction errors** — PDF parsing may miss clauses or tables | Medium | Medium | 🟡 High | Manual extraction for MVP; maintain source_registry with clause references; review with BNBC expert | Software Architect | Planned |
| RSK-006 | R-REG | **Users claim "RAJUK compliant" based on tool output** — tool only calculates metrics | High | High | 🔴 Critical | Never label "compliant"; display "Calculated FAR: 2.4 | DAP Limit: 3.4"; explicit disclaimer | Product/UX | Accepted |
| RSK-007 | R-TECH | **IFC geometry extraction failures in Phase 3** — complex BIM models | Medium | High | 🟡 High | Phase 3 only; validate with IfcOpenShell test suite; geometry repair pipeline | BIM Engineer | Deferred |
| RSK-008 | R-TECH | **Calculation engine results drift** — frontend/backend formula divergence | Medium | High | 🟡 High | Single source of truth (backend); shared test vectors (Python + JS); CI runs both | QA Engineer | Planned |
| RSK-009 | R-TECH | **Large file uploads (IFC) crash backend** — memory/timeout | Medium | Medium | 🟡 High | Size limits (10MB MVP, 100MB Phase 3); streaming upload; background processing | Backend Engineer | Planned |
| RSK-010 | R-USER | **Users treat screening results as verified** — ventilation/daylight are preliminary | High | High | 🔴 Critical | Mandatory confidence/limitation display on every result; "Preliminary" badge; no pass/fail green/red | UX Designer | Accepted |
| RSK-011 | R-USER | **Professional liability** — user relies on tool for design decisions | High | High | 🔴 Critical | Every report includes: "Preliminary analysis — requires professional review"; structural disclaimer | Legal/Compliance | Accepted |
| RSK-012 | R-USER | **AI assistant hallucinates codes** — AI integration risk | Medium | High | 🟡 High | Retrieval-grounded only; no API keys in frontend; cite sources; human-in-loop | AI Engineer | Planned |
| RSK-013 | R-SEC | **File upload malware / path traversal** | Medium | High | 🟡 High | File type validation; size limits; sandboxed processing; malware scan (Phase 2) | Security Engineer | Planned |
| RSK-014 | R-SEC | **API keys exposed in frontend** | Low | Critical | 🟡 High | All secrets server-side; no keys in repo; environment variables only | Backend Engineer | Planned |
| RSK-015 | R-PROJ | **Scope creep — adding simulation before baseline stable** | Medium | Medium | 🟡 High | Strict phase gates; MVP = deterministic only; simulation only after validation | PM | Accepted |
| RSK-016 | R-PROJ | **Insufficient test coverage for engineering formulas** | Medium | High | 🟡 High | Reference value tests for every formula; CI gate on test pass; pytest + JS tests | QA Engineer | Planned |
| RSK-017 | R-DATA | **BNBC occupancy minimums not clearly mapped to all room types** | Medium | Medium | 🟡 High | Map BNBC Ch 2 occupancy classes to room_type enum; document gaps | Building Eng | Planned |
| RSK-018 | R-DATA | **SREDA baseline EPI sample size small (30 buildings)** — not representative | Medium | Medium | 🟡 High | Flag as "sample-based"; sensitivity analysis; collect more data | Data Engineer | Accepted |
| RSK-019 | R-TECH | **Docker deployment fails on target environment** | Low | Medium | 🟢 Medium | Test deployment locally; document env vars; CI/CD pipeline | DevOps | Planned |
| RSK-020 | R-USER | **Low-bandwidth users cannot load EPW/visualization** | Medium | Low | 🟢 Medium | EPW cached server-side; lightweight SVG floor plan; optional heavy viz | Frontend | Planned |

## Risk Response Strategies

| Strategy | Risks Addressed |
|----------|-----------------|
| **Accept** | RSK-001, RSK-002, RSK-003, RSK-006, RSK-010, RSK-011, RSK-018 |
| **Mitigate** | RSK-004, RSK-005, RSK-007, RSK-008, RSK-009, RSK-012, RSK-013, RSK-014, RSK-016, RSK-017, RSK-019, RSK-020 |
| **Defer** | RSK-007 (to Phase 3) |
| **Monitor** | All risks reviewed each sprint |

## Monitoring & Escalation

- **Weekly**: Risk review in sprint planning
- **Bi-weekly**: Data source verification check
- **Per release**: Regression test suite execution
- **Escalation**: Any 🔴 Critical risk → PM + Tech Lead immediately

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*