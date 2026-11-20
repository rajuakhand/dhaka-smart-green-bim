# DhakaSmart Urban Density & Green BIM

> **Bangladesh Climate-Aware Building Performance & Space Optimization Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docs.docker.com/compose/)

A lightweight, scalable, evidence-driven web platform for preliminary building performance analysis in dense urban environments — starting with Dhaka, Bangladesh.

---

## 🎯 Mission

Help architects, engineers, developers, and researchers assess building design performance using **verified engineering rules, local climate data, deterministic calculations, and traceable sources** — not opaque estimates.

**Target users**: Architects, Civil Engineers, Building Developers, Urban Planners, Architecture Students, Energy Researchers, Sustainability Consultants.

---

## ✨ Core Features (MVP)

| Module | Capability | Data Source |
|--------|------------|-------------|
| **Building Setup** | Project metadata, building geometry, orientation, materials | User input + BNBC 2020 validation |
| **Room Analyzer** | Per-room geometry, occupancy, area/person, code checks | BNBC 2020 Part 3 Ch 2 |
| **Ventilation Screening** | Opening ratio, cross-ventilation potential, bottlenecks | BNBC Sec 2.14.6.1 (5% min) |
| **Daylight Screening** | Glazing ratio, obstruction, shading assessment | BNBC Sec 2.14.6.1 (10% min) |
| **Energy Estimator** | Preliminary cooling/lighting/equipment energy (kWh/m²/yr) | SREDA benchmarks + EPW |
| **Carbon Calculator** | Operational electricity emissions (kg CO₂e/yr) | DoE GEF 0.61-0.62 / Ember 0.696 |
| **Density & Urban Context** | FAR, ground coverage, open space, RAJUK DAP limits | RAJUK DAP 2022-2035 |
| **Structural Risk Screening** | Missing info flags, professional review reminders | BNBC Part 6 |
| **Design Optimization** | Baseline vs alternative comparison (window, shading, glazing, COP) | Same deterministic engine |

---

## 📋 Engineering Principles (Non-Negotiable)

1. **No fabricated data** — Every rule has a traceable source
2. **Deterministic calculations** — Testable, documented, unit-tested
3. **AI assists, never replaces** — AI only explains; never computes
4. **Uncertainty always shown** — Every result carries confidence + limitations
5. **Preliminary = preliminary** — No pass/fail; no simulation claims without simulation
6. **Professional review required** — Structural safety always needs qualified engineer

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend  │────▶│    Backend API   │────▶│  PostgreSQL +   │
│  (Next.js)  │     │   (FastAPI)      │     │  PostGIS        │
└─────────────┘     │                  │     └─────────────────┘
                    │ Calculation Eng. │
                    │  (Pure Python)   │
                    └──────────────────┘
```

**Frontend**: Next.js 14, TypeScript, Tailwind CSS, Zustand, SVG visualization
- **Backend**: FastAPI, SQLAlchemy + PostGIS, Pydantic v2
- **Calculations**: Isolated pure functions, 100% unit-tested with reference values
- **Phase 2**: pvlib (NREL SPA solar position, Ineichen-Perez clear-sky), CIBSE/BRE daylight factor, ISO 6946 U-values, NASA POWER climate API
- **Phase 3**: IfcOpenShell 0.8.1 (IFC parsing, unit scaling, swept-solid geometry, geometry validation, IFC→analysis model)
- **Data**: EPW cached locally, emission factors seeded, source registry CSV, NASA POWER cached in `data/climate/`

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker + Docker Compose (recommended)
- PostgreSQL 15+ with PostGIS (or use Docker)

### Option 1: Docker Compose (Recommended)

```bash
git clone https://github.com/rajuakhand/dhaka-smart-green-bim.git
cd dhaka-smart-green-bim
docker compose up -d
```

Access:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/docs`

### Option 2: Local Development

```bash
# Backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # configure DATABASE_URL
alembic upgrade head
uvicorn src.main:app --reload

# Frontend (new terminal)
cd web && npm install && npm run dev
```

---

## 📊 Verified Data Sources

| Source | Data | Verification |
|--------|------|--------------|
| **BNBC 2020** | Occupancy, ventilation (5%), daylight (10%), energy Ch 4 | ✅ Gazette 11 Feb 2021 |
| **RAJUK DAP 2022-2035** | FAR by zone, ground coverage by plot size, height limits | ✅ Gazette 24 Aug 2022 |
| **DoE Grid Emission Factor** | 0.61–0.62 tCO₂/MWh (2019–22) | ✅ Official letter 23 Jan 2025 |
| **Ember/OWID** | 0.696 kg CO₂e/kWh (2025) | ✅ CC BY 4.0, Ember |
| **World Bank BEEER Survey** | Residential EPI: 42 kWh/m²/yr | ⚠️ Sample of 30 buildings |
| **EnergyPlus EPW** | Dhaka TMYx (SWERA 419230) | ✅ NREL/DOE |
| **NASA POWER** | Hourly solar, met, 0.5° grid | ✅ Satellite-derived |
| **Chaudhary & Akhtar 2023** | 78 material GWP factors (India) | ✅ Peer-reviewed, marked geography |

> **Note**: No Bangladesh-specific construction EPDs exist yet. Embodied carbon is excluded from MVP.

---

## 📖 Documentation
| Document | Description |
| [Feasibility Analysis](docs/01_feasibility_analysis.md) | Technical, regulatory, data feasibility |
| [Detailed MVP Scope](docs/02_detailed_mvp_scope.md) | All modules, pages, data dictionary |
| [Excluded Features](docs/03_excluded_features.md) | What's NOT in MVP with rationale |
| [Architecture](docs/04_architecture_diagram.md) | System diagram, DB schema, data flow |
| [Data Collection Plan](docs/05_data_collection_plan.md) | Phase-wise data acquisition |
| [Source Verification](docs/06_source_verification_plan.md) | Source registry, verification workflow |
| [Data Dictionary](docs/07_data_dictionary.md) | All fields, schemas, reference tables |
| [Calculation Inventory](docs/08_calculation_inventory.md) | Every formula, test cases, references |
| [Risk Register](docs/09_risk_register.md) | 20 identified risks with mitigations |
| [Development Roadmap](docs/10_development_roadmap.md) | 18-month phased plan |
| [Folder Structure](docs/11_initial_folder_structure.md) | Repository layout |
| [Testing Plan](docs/12_testing_validation_plan.md) | Unit, integration, E2E, regression |

---

## 🔌 API Reference

All endpoints are prefixed with `/api/v1`. Interactive docs at `/docs`.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness |
| GET | `/sources` | Verified source registry |
| POST | `/projects` | Create project |
| POST | `/projects/{id}/rooms` | Add rooms |
| POST | `/projects/{id}/calculate` | Phase 1 full analysis |
| GET | `/projects/{id}/report?format=html` | HTML report |
| GET | `/phase2/simulation-capability` | Engine availability (honest) |
| GET | `/phase2/climate` | NASA POWER climate normals |
| POST | `/phase2/solar` | Solar geometry + facade exposure |
| POST | `/phase2/daylight` | CIBSE/BRE daylight factor |
| POST | `/phase2/shading` | Geometric shading analysis |
| POST | `/phase2/sensitivity` | One-at-a-time sensitivity |
| GET | `/phase2/materials` | ISO 6946 U-value database |
| POST | `/phase2/envelope` | Area-weighted envelope U-value |
| POST | `/phase2/projects/{id}/run` | Full Phase 2 analysis |
| GET | `/bim/capability` | IfcOpenShell availability |
| POST | `/bim/upload` | Upload an `.ifc` file |
| POST | `/bim/analyze` | Parse + validate + convert |
| POST | `/bim/projects/{id}/import` | Import IFC rooms into a project |
| GET | `/bim/schemas` | Supported IFC schemas and entities |

---

## 🖥️ Frontend Routes

| Route | Purpose |
|-------|---------|
| `/` | Landing page |
| `/dashboard` | Project overview |
| `/projects/new` | 4-step project wizard (validated client + server side) |
| `/projects/[id]` | Building setup (info, geometry, materials, site) |
| `/projects/[id]/rooms` | Room editor with live geometry |
| `/projects/[id]/floorplan` | SVG floor plan |
| `/analysis/overview` | Module results summary |
| `/analysis/{ventilation,daylight,energy,carbon,density,structural}` | Phase 1 module results |
| `/optimization` | Baseline vs alternatives |
| `/phase2` | Advanced analysis hub |
| `/phase2/{climate,solar,daylight,shading,sensitivity,optimization,materials}` | Phase 2 modules |
| `/bim` | IFC upload, model summary, extracted rooms |
| `/data-sources` | Verified source registry |
| `/settings` | Project defaults (emission factor, schedules) |
| `/report` | Report export |
| `/documentation` | Methodology and limitations |

---

## 🚧 Development Roadmap

### Phase 1 — MVP (✅ Complete)
| Module | Status |
|--------|--------|
| Building Setup (A) | ✅ Complete |
| Room Analyzer (B) | ✅ Complete |
| Ventilation Screening (C) | ✅ Complete |
| Daylight Screening (D) | ✅ Complete |
| Energy Estimator (E) | ✅ Complete |
| Carbon Calculator (F) | ✅ Complete |
| Density & Urban Context (G) | ✅ Complete |
| Structural Risk Screening (H) | ✅ Complete |
| Design Optimization (I) | ✅ Complete |
| FastAPI Backend | ✅ Complete |
| Next.js Frontend (17 pages) | ✅ Complete |
| 83 Unit Tests | ✅ All Passing |
| GitHub Repository | ✅ Published |

### Phase 2 — Advanced Analysis (✅ Complete)
Physics-based engineering calculations using verified astronomical models and
published methods. **No external simulation engine required** for these modules.

| Module | Method | Status |
|--------|--------|--------|
| Climate Data | NASA POWER monthly normals + BMD fallback | ✅ Complete |
| Solar Geometry | NREL SPA + Ineichen-Perez (pvlib) | ✅ Complete |
| Solar Heat Gain | Q = A × I × SHGC | ✅ Complete |
| Daylight Factor | CIBSE/SLL LG10 (BRE method) | ✅ Complete |
| Shading Analysis | Geometric profile angles | ✅ Complete |
| Sensitivity Analysis | One-at-a-time perturbation | ✅ Complete |
| Parametric Optimization | Exhaustive grid search | ✅ Complete |
| Material Database | ISO 6946 derived U-values | ✅ Complete |
| Simulation Bridge | Honest engine detection | ✅ Complete |
| Phase 2 UI (7 pages) | `/phase2/*` | ✅ Complete |
| 162 additional tests | Phase 2 suite | ✅ 245 total passing |

**Verified reference values** (all test-locked):
- Dhaka annual mean temp: **25.44 °C** (NASA POWER T2M, 2005–2024)
- Dhaka extreme max: **43.27 °C** / extreme min: **7.53 °C**
- Dhaka mean GHI: **4.225 kWh/m²/day**
- Equinox noon solar altitude: **66.41°** (= 90° − 23.81° latitude)
- Summer solstice noon altitude: **89.63°** (sun near-overhead at Dhaka)
- Clear-sky noon GHI: **907.5 W/m²** (Ineichen-Perez)
- 150 mm brick + plaster wall U-value: **2.413 W/m²K** (ISO 6946)
- Insulated wall U-value: **0.601 W/m²K**
- Daylight factor, 3 m² glazing in 5×4×3 m room: **1.687 %**
- AC COP is the most influential energy input (elasticity −0.543)

> **Engineering correction made during Phase 2:** NASA POWER's `T2M_MAX` /
> `T2M_MIN` are **extremes**, not mean daily max/min. The initial implementation
> averaged them to derive mean temperature, which overstated it (33.4 °C vs the
> correct 25.4 °C). Fixed by using `T2M` (true monthly mean) for mean
> temperature and CDD, with regression tests locking the correct behaviour.

> **EnergyPlus / Radiance are NOT installed.** Rather than fabricate output, the
> platform reports them as unavailable and marks the corresponding results
> **"Not evaluated"** — never "Simulated".

### Phase 3 — BIM Integration (✅ Complete)
Real IFC parsing via IfcOpenShell 0.8.1, with geometry validation and conversion
into the platform's analysis model. A BIM room flows straight into the Phase 1
and Phase 2 engines.

| Capability | Method | Status |
|------------|--------|--------|
| IFC upload (multipart, allowlisted, size-capped, name-sanitised) | FastAPI UploadFile | ✅ Complete |
| Schema detection | IFC2X3 / IFC4 / IFC4X3 | ✅ Complete |
| Unit scaling (mm → m) | IfcUnitAssignment parsing | ✅ Complete |
| Space / wall / slab / roof / window / door extraction | IfcOpenShell `by_type` | ✅ Complete |
| Geometry measurement | `IfcExtrudedAreaSolid` swept solids | ✅ Complete |
| Geometry validation (6 error + 4 warning + 2 note checks) | `validator.py` | ✅ Complete |
| IFC → analysis room model | `converter.py` | ✅ Complete |
| Room-type inference from space names | keyword map, flagged when unmatched | ✅ Complete |
| BIM → Phase 1 → Phase 2 → Report pipeline | API integration | ✅ Complete |
| Phase 3 UI (`/bim`) | upload + model summary + rooms table | ✅ Complete |
| 47 Phase 3 tests | `tests/test_bim.py` | ✅ 292 total passing |

**Two IFC fixtures, both locked to the same metric result** (`tests/fixtures/`):
- `sample_m.ifc` — length unit METRE, coordinates in metres
- `sample_mm.ifc` — length unit MILLI METRE, coordinates in millimetres

Both must parse to identical metric values. This guards against the classic
"room is 1000× too small" IFC bug:
```
sample_m.ifc    footprint=21.15 m²  room=20.0 m²  wall area=54.0 m²
sample_mm.ifc   footprint=21.15 m²  room=20.0 m²  wall area=54.0 m²
```

> **Engineering bug caught by these tests:** the initial footprint calculation
> added `max(x_dim, y_dim)` to each wall origin, which over-counted walls whose
> profile length runs along Y. A 5×4 m room reported a 76.9 m² footprint instead
> of 21.15 m². Fixed to a component-wise bounding box.

> **IfcOpenShell 0.8.1 is pinned on purpose.** The 0.9.x wheels are built
> against `GLIBCXX_3.4.29`; on hosts whose `libstdc++` stops at 3.4.28 (this
> one) they install but fail to import. 0.8.1 works on a much wider range of
> hosts. If IfcOpenShell is unavailable, every BIM endpoint returns
> `{"executed": false, "status": "Not evaluated"}` — never fabricated model data.

### Phase 4 — Advanced Simulation (📅 Future)
| Sprint | Focus | Deliverables |
|--------|-------|--------------|
| 4.1 | EnergyPlus integration (local) | EnergyPlus simulation bridge |
| 4.2 | Radiance integration | Daylight simulation bridge |
| 4.3 | CFD integration assessment | Feasibility study, no code in MVP |

---

## 🧪 Testing

```bash
# Backend (292 tests, all passing)
pytest tests/ -v --cov=src --cov-report=term-missing

# Frontend unit tests (33 tests: wizard validation, payload, review rows)
cd web && npm test

# Frontend typecheck
cd web && npx tsc --noEmit

# End-to-end UI tests (3 tests, needs a running dev server + backend)
cd web && BASE_URL=http://localhost:3000 API_URL=http://localhost:8000 npx playwright test

# Security
bandit -r src/
ruff check src/
```

**Phase 1 Gate**: 100% formula coverage, all reference values pass, zero security HIGH/CRITICAL.
**Phase 2 Gate**: 245 tests passing including 162 Phase 2 reference tests.
**Phase 3 Gate**: 292 backend tests + 33 frontend unit tests + 3 E2E tests passing.

---

## 🔒 Security & Privacy

- **No secrets in code** — All via environment variables
- **Input sanitization** — Pydantic + server-side validation
- **File upload safety** — Size limits, type checking, sandboxed processing
- **No PII in logs** — Structured logging with redaction
- **AI grounding** — Retrieval-only, no API keys in frontend

---

## 📜 License

MIT License — see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **Bangladesh National Building Code 2020** — MoPHW, RAJUK
- **SREDA** — Building Energy Efficiency & Environment Rating
- **Ember / Our World in Data** — Electricity carbon intensity
- **NASA POWER** — Satellite meteorological data
- **EnergyPlus / NREL** — Weather file standards
- **Chaudhary & Akhtar (2023)** — ICMD material factors
- **World Bank** — BEEER baseline surveys

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## ⚠️ Disclaimer

> **This platform provides PRELIMINARY analysis only.** Results are based on screening-level calculations with documented assumptions and limitations. They are **NOT** a substitute for:
> - Verified structural assessment
> - Certified energy simulation (EnergyPlus, Radiance)
> - Professional engineering review
> - Regulatory compliance certification
>
> Always engage qualified professionals for design decisions.

---

**Made with 🇧🇩 for Bangladesh's sustainable urban future.**

---

> **Web app (recommended):** https://rajuakhand.github.io/dhaka-smart-green-bim/  
> **Source code:** https://github.com/rajuakhand/dhaka-smart-green-bim  
> **Documentation:** https://github.com/rajuakhand/dhaka-smart-green-bim/wiki