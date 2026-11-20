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

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Zustand, SVG visualization
- **Backend**: FastAPI, SQLAlchemy + PostGIS, Pydantic v2
- **Calculations**: Isolated pure functions, 100% unit-tested with reference values
- **Data**: EPW cached locally, emission factors seeded, source registry CSV

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
|----------|-------------|
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

## 🧪 Testing

```bash
# Backend
pytest tests/ -v --cov=src --cov-report=term-missing

# Frontend
cd web && npm test

# Security
bandit -r src/
ruff check src/
```

**Phase 1 Gate**: 100% formula coverage, all reference values pass, zero security HIGH/CRITICAL.

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