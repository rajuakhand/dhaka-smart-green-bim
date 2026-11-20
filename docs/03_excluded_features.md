# Features Excluded from MVP

## Excluded Features and Rationale

| Feature | Why Excluded from MVP | Minimum Data/Dependency to Include | Target Phase |
|---------|----------------------|-----------------------------------|--------------|
| **Hourly energy simulation (EnergyPlus)** | Requires stable IDF model, input geometry validation, and trained simulation engineer. MVP must first establish geometry + calc engine. | Validated IDF model, EPW file, and simulation results from Phase 1 baseline | Phase 2 |
| **sDA / ASE daylight metrics** | Requires Radiance simulation. Simple WWR screening is sufficient for MVP. | Radiance engine, materials library, and 3D model | Phase 2 |
| **Advanced shading analysis** | Requires geometric obstruction calculation (overhang/fin/neighbor). MVP uses binary "external obstruction" flag. | 3D obstruction geometry, shadow simulation | Phase 2 |
| **Sensitivity analysis** | Requires stable baseline results to perturb against. No value until baseline is solid. | Monte Carlo / one-at-a-time framework | Phase 2 |
| **Parametric design optimization** | Requires optimization algorithm (genetic/annealing) + stable baseline. Not for MVP. | DOE/optimization framework, cost model | Phase 2 |
| **Surrounding building obstruction** | Requires 3D city model (OSM or LIDAR). MVP uses flat "obstruction height" input. | OSM 3D extract or LIDAR-derived heights | Phase 2 |
| **CFD / airflow modeling** | Requires validated airflow model and expert judgment. Not justified for MVP. | CFD engine (OpenFOAM), boundary conditions, mesh | Phase 3 only if justified |
| **Embodied carbon** | No verified Bangladesh-specific EPDs. Indian ICMD factors are unverified for Bangladesh geography. | Bangladesh EPD registry or peer-reviewed LCA study | Phase 2 (with flag) |
| **IFC upload / BIM extraction** | Requires stable geometry input model. IFC parsing is complex and needs dedicated validation. | IfcOpenShell + geometry validation suite | Phase 3 |
| **GIS zone lookup for RAJUK DAP** | Requires GeoJSON shapefiles or tile server. MVP uses manual zone selection. | RAJUK DAP zone layer + server | Phase 2 |
| **Market-based emission factors** | Compliance reporting needs location-based Scope 2. Market-based is optional for green marketing. | User-selected market-based factors + documentation | Phase 2 |
| **Embodied carbon transport** | Requires mass-based transport modeling. Not for MVP. | Transport distance, mass, transport factor | Phase 2+ |
| **End-of-life carbon** | Requires waste disposal assumptions and demolition factors. Not for MVP. | Demolition factors, waste classification | Phase 2+ |
| **Water consumption modeling** | Separate from energy/carbon scope. MVP focuses on energy and carbon. | Water fixtures, occupancy, usage patterns | Phase 2 |
| **Landscaping / roof garden analysis** | Requires vegetation database and irrigation model. Not core to energy/carbon. | Plant species, growth model, irrigation | Phase 2+ |
| **User accounts / project persistence** | MVP can be stateless (client-side computation). Server persistence is Phase 2. | Database schema + auth | Phase 2 |

## Explicit MVP Boundaries (What the System WILL NOT Do)

1. **Never claim structural safety** — Module H is a risk screening only
2. **Never claim verified lux levels, sDA, or ASE** — Daylight screening uses WWR ratio only
3. **Never claim verified air-change rate** — Ventilation screening uses opening ratio only
4. **Never mix preliminary and simulation modes** — MVP only has "preliminary" mode
5. **Never report simulated values as measured** — All results are "preliminary" unless explicitly simulated
6. **Never declare RAJUK compliance** — Density module calculates metrics but does not verify compliance
7. **Never use one universal occupancy limit** — Room types have specific occupancy references

---
*Document Version: 1.0 | Date: 2026-11-20 | Status: DRAFT for Review*