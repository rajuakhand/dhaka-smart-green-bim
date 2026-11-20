# Development Roadmap

## Overall Timeline: 18 Months (Phase-gated)

### Phase 0 — Research & Specification (Month 1-2)
| Sprint | Activity | Deliverables |
|--------|----------|--------------|
| 0.1 | Complete project charter, scope, architecture | This document set |
| 0.2 | Source verification (Tier 1-2) | source_registry.csv populated, statuses set |
| 0.3 | Data acquisition plan + EPW download | EPW cached, emission factors stored |
| 0.4 | Calculation specification draft | Formula inventory with references |

### Phase 1 — MVP (Month 3-12)
| Sprint | Focus | Deliverables | Exit Criteria |
|--------|-------|--------------|---------------|
| 1.1 | Project foundation | FastAPI + Next.js skeleton, DB schema, validation | CI green, Docker Compose runs |
| 1.2 | Building + Room modules | Forms, geometry validation, room analysis | 10+ unit tests pass |
| 1.3 | Ventilation + Daylight modules | Screening formulas, recommendations | 15+ unit tests pass |
| 1.4 | Energy + Carbon modules | Preliminary energy estimate, carbon calculation | 20+ unit tests pass |
| 1.5 | Density + Structural + Optimization | All modules integrated | 30+ unit tests pass |
| 1.6 | Frontend integration (17 pages) | UI for all modules, dashboard, before/after | UI tests pass, no console errors |
| 1.7 | Report export | PDF/CSV with full provenance | Report generation tested |
| 1.8 | Security + compliance review | Input sanitization, confidentiality, disclaimers | Security checklist pass |

### Phase 2 — Advanced Analysis (Month 13-18)
| Sprint | Focus | Deliverables |
|--------|-------|--------------|
| 2.1 | Weather-based analysis UI | EPW station selector, climate summary |
| 2.2 | Hourly energy simulation integration | EnergyPlus API bridge (external) |
| 2.3 | Advanced daylight (sDA/ASE) | Radiance integration (external) |
| 2.4 | Advanced shading | 3D obstruction calculation |
| 2.5 | Design optimization (parametric) | DOE / optimization engine |
| 2.6 | Sensitivity analysis | Baseline + perturbations |
| 2.7 | Embodied carbon (fallback ICMD flagged) | Embodied module |

### Phase 3 — BIM Integration (Month 19-22)
| Sprint | Focus | Deliverables |
|--------|-------|--------------|
| 3.1 | IFC upload + validation | Secure upload, size/type checks |
| 3.2 | BIM geometry extraction | IfcOpenShell parsing, wall/floor/roof/window extraction |
| 3.3 | Geometry validation | Consistency checks |
| 3.4 | IFC-to-analysis model | Normalized room/space data |

### Phase 4 — Advanced Simulation (Month 23-26)
| Sprint | Focus | Deliverables |
|--------|-------|--------------|
| 4.1 | EnergyPlus integration (local) | EnergyPlus simulation bridge |
| 4.2 | Radiance integration | Daylight simulation bridge |
| 4.3 | CFD integration assessment | Feasibility study, no code in MVP |

### Phase 5 — Deployment & Launch (Month 27-30)
| Sprint | Focus | Deliverables |
|--------|-------|--------------|
| 5.1 | Production deployment | Docker, env vars, DB migrations, deploy guide |
| 5.2 | Backup strategy | Backup + restore procedures |
| 5.3 | User guide | Onboarding docs |
| 5.4 | Validation report | Final QA + performance |

## Milestones

| Milestone | Target | Exit Criteria |
|-----------|--------|---------------|
| M0 | Month 2 | Architecture + specs approved |
| M1 | Month 12 | MVP shipped with all 9 modules working |
| M2 | Month 18 | Phase 2 core features shipped |
| M3 | Month 22 | Phase 3 BIM module beta |
| M4 | Month 26 | Phase 4 simulation bridges integrated |
| M5 | Month 30 | Public release / deployment |

## MVP Gate Criteria (Go/No-Go for Phase 1 Ship)

- ✅ All 9 modules produce deterministic results
- ✅ Every calculation has reference tests + passing regression suite
- ✅ Every result carries confidence + limitations + sources
- ✅ No green/red pass/fail without simulation
- ✅ Professional review disclaimers on reports
- ✅ No fabricated data values
- ✅ Security review passed
- ✅ Documentation for methodology complete

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*