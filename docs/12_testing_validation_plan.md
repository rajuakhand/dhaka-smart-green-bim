# Testing and Validation Plan

## Test Strategy

| Level | Framework | Scope | Target Coverage |
|-------|-----------|-------|-----------------|
| Unit (Python) | pytest | Calculation modules, data validation | 100% of formulas |
| Unit (JS) | Vitest / Jest | Frontend calculation mirror, types | 100% of formulas |
| Integration | pytest + TestClient | API endpoints, DB operations | All API routes |
| E2E | Playwright | Critical user flows | Top 10 journeys |
| Security | Bandit / Semgrep | Code scanning | CI gate |
| Performance | Locust | API response times | p95 < 500ms |

## Test Categories

### 1. Calculation Unit Tests (Mandatory — Every Formula)

| Module | Formula | Test Cases | Reference Values |
|--------|---------|------------|------------------|
| A | Footprint fits plot | Normal, boundary (footprint == plot), invalid | True/False |
| B | Floor Area | Normal (L=5,W=4→20), boundary (L=1,W=1), invalid (neg) | 20 m² |
| B | Volume | Normal (Area=20,H=3→60), boundary (H=2) | 60 m³ |
| B | Area per Person | Normal (Area=20,Occ=2→10), boundary (Occ=1), invalid (Occ=0) | 10 m²/pers |
| B | Occupancy BNBC | Pass (10 > 9.3), Fail (8 < 9.3), boundary (9.3) | Pass/Fail |
| C | Opening Ratio | Normal (5% → 5%), boundary (5%), invalid (neg) | 5% |
| C | Room Depth Ratio | Normal (Depth=5,H=3→1.67) | 1.67 |
| D | Glazing Ratio | Normal (10% → 10%), boundary (10%), fail (8%) | Pass/Fail |
| E | Cooling Energy | Normal (COP=3, kW=5, hrs=1800→30000) | 30000 kWh |
| E | Lighting Energy | Normal (7 W/m² × 100 m² × 2500h → 1750) | 1750 kWh |
| E | Equipment Energy | Normal (5 W/m² × 100 × 2500 → 1250) | 1250 kWh |
| E | Total EPI | Sum components / area | 52.1 kWh/m²/yr |
| F | Carbon | 125000 × 0.696 → 87000 kg | 87000 kg CO₂e |
| G | FAR | 2400 m² / 1000 m² → 2.4 | 2.4 |
| G | Ground Coverage | 500 / 1000 → 50% | 50% |
| G | Open Space | (1000-500)/1000 → 50% | 50% |
| I | Delta Absolute | Alt=44.3, Base=52.1 → -7.8 | -7.8 |
| I | Delta Percent | -7.8 / 52.1 × 100 → -15% | -15% |

### 2. Boundary & Edge Case Tests (Per Formula)

| Category | Examples |
|----------|----------|
| Zero values | Area = 0, Occupants = 0, Window area = 0 |
| Negative inputs | Should return ValidationError |
| Maximum realistic | Floor=50, Height=15, FAR=20 |
| Unit conversion | m² vs ft² (reject non-SI) |
| Precision | Decimal places in results (2 for areas, 3 for ratios) |

### 3. Missing Data Tests

| Scenario | Expected Behavior |
|----------|-------------------|
| Missing room height | Result: `Insufficient` with limitation noted |
| Missing occupancy schedule | Use default (Daytime); log assumption |
| Missing EPW | Energy mode: `Not evaluated` |
| Missing emission factor source | Require user selection; no default calculation |

### 4. Regression Tests (Reference Values)

| Test | Baseline Input | Expected Output | Tolerance |
|------|----------------|-----------------|-----------|
| Residential 6-story EPI | 6 floors, 200 m²/floor, COP=3.1, lighting=7, equip=5 | ~52 kWh/m²/yr | ±5% |
| Carbon 125,000 kWh | Ember 0.696 | 87,000 kg CO₂e | Exact |
| FAR 3 floors | 1000 m² plot, 600 m² footprint, 3 floors | 1.8 | Exact |

### 5. Integration Tests (API)

| Endpoint | Test Cases |
|----------|------------|
| POST /projects | Valid project, invalid missing fields, duplicate name |
| GET /projects/{id} | Existing, not found |
| POST /projects/{id}/rooms | Valid room, geometry mismatch, missing fields |
| POST /projects/{id}/calculate | All modules, partial modules, missing data |
| GET /projects/{id}/report | PDF export, CSV export, missing results |

### 6. Frontend Tests (JS)

| Test | Description |
|------|-------------|
| Form validation | Zod schema matches Pydantic |
| Calculation mirror | Same formula results as backend (shared test vectors) |
| Confidence display | Shows High/Medium/Low/Insufficient correctly |
| Report preview | Renders sections correctly |

### 7. Data Validation Tests

| Data Source | Validation Rules |
|-------------|------------------|
| EPW | 8760 rows, valid headers, no NaN in core fields |
| Source registry | All required columns, no duplicate source_id |
| Emission factors | Factor > 0, year reasonable, source not empty |
| BNBC rules | Rule_id unique, formula parseable |

## Test Execution Pipeline

```yaml
# .github/workflows/ci.yml (Conceptual)
jobs:
  test-backend:
    steps:
      - pytest tests/ -v --cov=src --cov-report=term-missing
      - pytest tests/ -k "calculation" --tb=short
  test-frontend:
    steps:
      - npm test -- --run --reporter=verbose
  lint:
    steps:
      - ruff check src/
      - mypy src/
      - npm run lint
  security:
    steps:
      - bandit -r src/
      - semgrep scan --config=auto src/
```

## Acceptance Criteria for Phase 1 Release

| Criterion | Threshold |
|-----------|-----------|
| Calculation unit tests | 100% of formulas covered, 100% pass |
| Integration tests | 100% API routes covered |
| Regression tests | All reference values within tolerance |
| Security scan | Zero HIGH/CRITICAL findings |
| Linting | Zero errors |
| Type checking | Zero mypy errors |
| E2E critical paths | All 10 flows pass |
| Documentation | All modules have method docs |

## Validation Reports

Each release generates:
1. **Calculation Validation Report** — All reference tests + pass/fail
2. **Data Quality Report** — EPW completeness, source registry status
3. **Security Scan Report** — Bandit/Semgrep findings
4. **Performance Report** — API latency, bundle size

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*