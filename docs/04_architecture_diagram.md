# Architecture Diagram: DhakaSmart Urban Density & Green BIM

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DHAKASMART SYSTEM ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────────────────────┐  │
│  │   FRONTEND   │────▶│                   BACKEND API                     │  │
│  │  (Next.js)   │     │                 (FastAPI)                         │  │
│  │              │     │                                                   │  │
│  │ ┌──────────┐ │     │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │  │
│  │ │  Pages   │ │     │  │ Project │ │  Calc   │ │  Data   │ │  Report │ │  │
│  │ │ (17 pg)  │ │     │  │ Service │ │ Engine  │ │ Service │ │ Service │ │  │
│  │ └──────────┘ │     │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ │  │
│  │ ┌──────────┐ │     │       │         │         │         │         │  │
│  │ │Components│ │     │       ▼         ▼         ▼         ▼         │  │
│  │ │(UI lib)  │ │     │  ┌─────────────────────────────────────────┐  │  │
│  │ └──────────┘ │     │  │        CALCULATION MODULES              │  │  │
│  └──────────────┘     │  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐   │  │  │
│         │             │  │  │ A  │ │ B  │ │ C  │ │ D  │ │ E  │   │  │  │
│         ▼             │  │  │    │ │    │ │    │ │    │ │    │   │  │  │
│  ┌──────────────┐     │  │  │ F  │ │ G  │ │ H  │ │ I  │     │   │  │  │
│  │   STATE      │     │  │  └────┘ └────┘ └────┘ └────┘ └────┘   │  │  │
│  │  (Zustand)   │     │  └─────────────────────────────────────────┘  │  │
│  └──────────────┘     │              │         │         │            │  │
└───────────┬───────────┘              ▼         ▼         ▼            ▼  │
            │                 ┌────────────────────────────────────────────┐ │
            │                 │              DATA LAYER                     │ │
            │                 │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │ │
            │                 │  │PostgreSQL│ │  File    │ │  EPW/    │    │ │
            │                 │  │ (PostGIS)│ │  Storage │ │  Weather │    │ │
            │                 │  │  Projects│ │  (IFC,   │ │  Cache   │    │ │
            │                 │  │  Rooms,  │ │  Reports,│ │          │    │ │
            │                 │  │  Results │ │  Uploads)│ │          │    │ │
            │                 │  └──────────┘ └──────────┘ └──────────┘    │ │
            │                 └────────────────────────────────────────────┘ │
            │                                 │                              │
            ▼                                 ▼                              ▼
       ┌────────────────────────────────────────────────────────────────────┐
       │                    EXTERNAL SERVICES / DATA                        │
       │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
       │  │ NASA POWER  │ │ EnergyPlus  │ │ Climate.    │ │ IfcOpenShell│ │
       │  │ API         │ │ (Phase 2)   │ │ OneBuilding │ │ (Phase 3)   │ │
       │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
       └────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Next.js 14 + TypeScript + Tailwind CSS)
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 14 (App Router) | SSR/SSG for performance, SEO |
| Language | TypeScript 5.x | Type safety for engineering data |
| Styling | Tailwind CSS + shadcn/ui | Accessible, consistent components |
| State | Zustand | Lightweight state for project/room data |
| Visualization | SVG (floor plan) + Chart.js | Lightweight, no WebGL dependency |
| Forms | React Hook Form + Zod | Client + server validation sync |
| Export | jsPDF + html2canvas / CSV | Report generation |

### Backend API (FastAPI + Python 3.11)
| Service | Module | Responsibility |
|---------|--------|----------------|
| Project Service | `/projects` | CRUD for project metadata, versioning |
| Room Service | `/projects/{id}/rooms` | Room CRUD, geometry validation |
| Calculation Engine | `/projects/{id}/calculate` | Runs Modules A-I deterministically |
| Data Service | `/data/*` | EPW cache, material registry, emission factors |
| Report Service | `/projects/{id}/report` | PDF/CSV generation with provenance |
| Auth Service | `/auth` | JWT-based (Phase 2); MVP: stateless |

### Calculation Engine Architecture (Deterministic, Testable)

```
┌────────────────────────────────────────────────────────────────┐
│                    CALCULATION ENGINE                           │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input Validation (Pydantic Models)                            │
│       │                                                         │
│       ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  ORCHESTRATOR: runs modules in dependency order         │   │
│  │  A → B → [C, D, G] → E → F → I                          │   │
│  └────────────────────────────────────────────────────────┘   │
│       │                                                         │
│       ▼                                                         │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌──┐ │
│  │  A  │ │  B  │ │  C  │ │  D  │ │  E  │ │  F  │ │  G  │ │H │ │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └──┘ │
│  Each module:                                                   │
│  - Pure functions (no side effects)                            │
│  - Returns: Result + Confidence + Source + Limitations          │
│  - Unit-tested with reference values                           │
│  └────────────────────────────────────────────────────────┘    │
```

### Database Schema (PostgreSQL + PostGIS)

```sql
-- Core tables (MVP)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    building_name TEXT,
    city TEXT DEFAULT 'Dhaka',
    building_type TEXT NOT NULL,
    num_floors INT NOT NULL,
    floor_to_floor_height NUMERIC NOT NULL,
    floor_area NUMERIC NOT NULL,
    orientation_deg NUMERIC NOT NULL,
    construction_year INT,
    structural_system TEXT,
    plot_area NUMERIC,
    building_footprint GEOMETRY(POLYGON, 4326), -- PostGIS
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    room_type TEXT NOT NULL,
    length NUMERIC NOT NULL,
    width NUMERIC NOT NULL,
    height NUMERIC NOT NULL,
    window_area NUMERIC DEFAULT 0,
    openable_window_area NUMERIC DEFAULT 0,
    occupants INT NOT NULL,
    occupancy_schedule TEXT,
    orientation_deg NUMERIC,
    glazing_type TEXT,
    external_obstruction_height NUMERIC DEFAULT 0,
    shading_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE calculation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    module_id TEXT NOT NULL, -- A, B, C, D, E, F, G, H, I
    version INT NOT NULL DEFAULT 1,
    input_snapshot JSONB NOT NULL,
    result JSONB NOT NULL,
    confidence TEXT NOT NULL, -- High, Medium, Low, Insufficient
    limitations TEXT[],
    source_references TEXT[],
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reference data (seeded)
CREATE TABLE emission_factors (
    id SERIAL PRIMARY KEY,
    source_id TEXT NOT NULL, -- 'DoE-GEF', 'Ember-OWID'
    year INT NOT NULL,
    factor_kg_co2_per_kwh NUMERIC NOT NULL,
    scope TEXT NOT NULL, -- 'location-based', 'generation-based'
    is_default BOOLEAN DEFAULT FALSE,
    verified BOOLEAN DEFAULT FALSE,
    source_url TEXT
);

CREATE TABLE bnbc_rules (
    id SERIAL PRIMARY KEY,
    rule_id TEXT NOT NULL UNIQUE, -- e.g., 'BNBC-2020-2.14.6.1'
    section TEXT NOT NULL,
    description TEXT NOT NULL,
    formula TEXT,
    required_inputs TEXT[],
    applicability TEXT,
    verified BOOLEAN DEFAULT FALSE
);

CREATE TABLE weather_stations (
    id SERIAL PRIMARY KEY,
    wmo_code TEXT UNIQUE,
    city TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    elevation NUMERIC,
    epw_source TEXT,
    epw_path TEXT,
    tm_years TEXT[] -- e.g., '{2007,2008,...}'
);
```

### Data Flow (MVP)

```
1. USER INPUT (Frontend forms)
       │
       ▼
2. CLIENT-SIDE VALIDATION (Zod schemas)
       │
       ▼
3. API REQUEST (POST /projects/{id}/calculate)
       │
       ▼
4. SERVER-SIDE VALIDATION (Pydantic)
       │
       ▼
5. CALCULATION ENGINE (Pure functions)
       │
       ├── Module A: Building Setup → validated context
       ├── Module B: Room Analyzer → area, volume, density
       ├── Module C: Ventilation Screening → opening ratios, flags
       ├── Module D: Daylight Screening → WWR, glazing, obstruction
       ├── Module E: Energy Estimator → kWh/m²/yr (preliminary)
       ├── Module F: Carbon Calculator → kg CO₂e/yr
       ├── Module G: Density & Urban Context → FAR, coverage, open space
       ├── Module H: Structural Risk Screening → missing info flags
       └── Module I: Optimization Comparison → delta from baseline
       │
       ▼
6. PERSIST RESULTS (PostgreSQL calculation_results)
       │
       ▼
7. RETURN FULL RESULT SET + METADATA (confidence, sources, limitations)
       │
       ▼
8. FRONTEND RENDER (Dashboard + individual module views)
       │
       ▼
9. REPORT EXPORT (PDF/CSV with full provenance)
```

### Deployment Architecture (MVP)

```
┌────────────────────────────────────────────────────────────┐
│                   DOCKER COMPOSE (Local / VPS)             │
├────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Frontend │  │  Backend │  │PostgreSQL│  │  Nginx   │  │
│  │ (Next.js)│  │ (FastAPI)│  │ + PostGIS│  │ (Reverse │  │
│  │  Port 3000│  │ Port 8000│  │ Port 5432│  │  Proxy)  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│       │            │            │            │            │
│       └────────────┴────────────┴────────────┘            │
│                    │                                      │
│              ┌─────┴─────┐                                 │
│              │  Volumes  │                                 │
│              │ - pg_data │                                 │
│              │ - uploads │                                 │
│              │ - epw     │                                 │
│              └───────────┘                                 │
└────────────────────────────────────────────────────────────┘
```

### Security Boundaries

| Boundary | Protection |
|----------|------------|
| Frontend → Backend | HTTPS, JWT (Phase 2), CORS |
| File Upload | Size limit (10MB MVP), type check (.ifc), malware scan (Phase 2) |
| Database | Parameterized queries, least privilege, no PII in logs |
| EPW Cache | Read-only after download, integrity checksum |
| AI Assistant (Phase 2) | No API keys in frontend; server-side proxy; retrieval-grounded only |

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*