# Initial Folder Structure

## Target Repository Structure (Phase 1)

```
dhaka-smart-green-bim/
├── docs/                                   # Planning & specification documents
│   ├── 01_feasibility_analysis.md
│   ├── 02_detailed_mvp_scope.md
│   ├── 03_excluded_features.md
│   ├── 04_architecture_diagram.md
│   ├── 05_data_collection_plan.md
│   ├── 06_source_verification_plan.md
│   ├── 07_data_dictionary.md
│   ├── 08_calculation_inventory.md
│   ├── 09_risk_register.md
│   ├── 10_development_roadmap.md
│   └── README.md
├── src/                                     # Backend Python package
│   ├── __init__.py
│   ├── main.py                              # FastAPI app factory
│   ├── config.py                            # Settings/env
│   ├── api/
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── rooms.py
│   │   ├── calculations.py
│   │   └── reports.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   └── logger.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── room.py
│   │   └── result.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── project_service.py
│   │   ├── room_service.py
│   │   ├── calculation_service.py
│   │   ├── data_service.py
│   │   └── report_service.py
│   ├── modules/                             # Deterministic calculation modules
│   │   ├── __init__.py
│   │   ├── building_setup.py
│   │   ├── room_analyzer.py
│   │   ├── ventilation.py
│   │   ├── daylight.py
│   │   ├── energy.py
│   │   ├── carbon.py
│   │   ├── density.py
│   │   ├── structural.py
│   │   └── optimization.py
│   └── sources/                             # Source registry data
│       ├── __init__.py
│       └── registry.py
├── tests/                                   # Backend tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_building_setup.py
│   ├── test_room_analyzer.py
│   ├── test_ventilation.py
│   ├── test_daylight.py
│   ├── test_energy.py
│   ├── test_carbon.py
│   ├── test_density.py
│   ├── test_structural.py
│   ├── test_optimization.py
│   ├── test_data_validation.py
│   └── test_geometry.py
├── data/                                    # Reference data (CSV/JSON)
│   ├── source_registry.csv
│   ├── emission_factors.csv
│   ├── bnbc_rules.csv
│   ├── weather/
│   │   └── Dhaka_419230.epw
│   └── climate/
│       └── dhaka_monthly.json
├── web/                                    # Frontend (Next.js 14)
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                       # Landing
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── projects/
│   │   │   ├── new/
│   │   │   │   └── page.tsx
│   │   │   └── [id]/
│   │   │       ├── page.tsx               # Building setup
│   │   │       ├── rooms/
│   │   │       │   └── page.tsx           # Room editor
│   │   │       ├── calculations/
│   │   │       │   └── page.tsx           # Module views
│   │   │       └── report/
│   │   │           └── page.tsx           # Report export
│   │   └── ...
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   └── results/
│   ├── lib/
│   │   ├── api.ts
│   │   ├── calculationEngine.ts
│   │   └── types.ts
│   └── ...
├── scripts/                                 # Operational scripts
│   ├── sync_web_data.py
│   ├── validate_sources.py
│   └── run_tests.sh
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── .github/workflows/                      # CI/CD
│   ├── ci.yml
│   └── deploy.yml
├── tests/                                   # Root-level integration tests
├── requirements.txt
├── pyproject.toml
├── README.md
└── AGENTS.md
```

## Key Decisions

1. **Backend calculation engine is source of truth** — Frontend only for UI; recomputes via API
2. **Pure functions for calculations** — easy to test, no side effects
3. **JSONB results** — flexible for module outputs; typed via Pydantic
4. **EPW cached locally** — offline-capable MVP
5. **PostgreSQL + PostGIS** — for geometry/planning data

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*