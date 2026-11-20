"""
Reports API — endpoints for generating downloadable reports.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from src.api.projects import _projects
from src.api.rooms import _rooms
from src.services.calculation_service import run_full_analysis

router = APIRouter()


def _generate_report_html(envelope, project, rooms) -> str:
    """Generate a self-contained HTML report from the calculation envelope."""
    e = envelope
    modules = e.modules

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DhakaSmart Report — {project.name}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #1a1a2e; line-height: 1.6; }}
  h1 {{ color: #0f3460; border-bottom: 3px solid #e94560; padding-bottom: .5rem; }}
  h2 {{ color: #0f3460; margin-top: 2rem; }}
  h3 {{ color: #16213e; }}
  .disclaimer {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 1rem; margin: 1.5rem 0; }}
  .confidence {{ display: inline-block; padding: .2rem .6rem; border-radius: .3rem; font-size: .85rem; font-weight: 600; }}
  .conf-high {{ background: #d4edda; color: #155724; }}
  .conf-med {{ background: #fff3cd; color: #856404; }}
  .conf-low {{ background: #f8d7da; color: #721c24; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  th, td {{ text-align: left; padding: .6rem .5rem; border-bottom: 1px solid #dee2e6; }}
  th {{ background: #f8f9fa; }}
  .metric {{ font-size: 2rem; font-weight: 700; color: #e94560; }}
  .limitation {{ color: #6c757d; font-style: italic; font-size: .9rem; }}
  footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #dee2e6; color: #6c757d; font-size: .85rem; }}
</style>
</head>
<body>

<h1>DhakaSmart Urban Density &amp; Green BIM</h1>
<h3>Building Performance Analysis Report</h3>

<div class="disclaimer">
  <strong>⚠️ PRELIMINARY ANALYSIS — NOT A CERTIFICATE</strong><br>
  {e.disclaimer}
</div>

<h2>Project: {project.name}</h2>
<table>
  <tr><th>Building Type</th><td>{project.building_type.value}</td></tr>
  <tr><th>City</th><td>{project.city}</td></tr>
  <tr><th>Number of Floors</th><td>{project.num_floors}</td></tr>
  <tr><th>Floor-to-Floor Height</th><td>{project.floor_to_floor_height_m} m</td></tr>
  <tr><th>Calculated At</th><td>{e.calculated_at.strftime('%Y-%m-%d %H:%M UTC')}</td></tr>
</table>

<h2>Energy Analysis (Preliminary)</h2>
<h3>Overall: {e.overall_confidence}</h3>
<p class="metric">{modules['E_energy']['total_electricity_kwh_per_year']:,.0f} kWh/year</p>
<p>Energy Performance Index: <strong>{modules['E_energy']['energy_performance_index_kwh_m2']} kWh/m²/yr</strong></p>
<table>
  <tr><th>End Use</th><th>Energy (kWh/yr)</th></tr>
  <tr><td>Cooling</td><td>{modules['E_energy']['breakdown']['cooling_kwh']:,.0f}</td></tr>
  <tr><td>Lighting</td><td>{modules['E_energy']['breakdown']['lighting_kwh']:,.0f}</td></tr>
  <tr><td>Equipment</td><td>{modules['E_energy']['breakdown']['equipment_kwh']:,.0f}</td></tr>
</table>
<p class="limitation">{'; '.join(modules['E_energy']['limitations'])}</p>

<h2>Operational Carbon Emissions</h2>
<p class="metric">{modules['F_carbon']['operational_emissions_t_co2e_per_year']} t CO₂e/year</p>
<p>Emission Factor: {modules['F_carbon']['emission_factor_kg_co2_per_kwh']} kg CO₂e/kWh ({modules['F_carbon']['emission_factor_source']}, {modules['F_carbon']['emission_factor_year']})</p>
<p>Embodied Carbon: <strong>Not calculated</strong> (no verified Bangladesh EPDs available)</p>
<p class="limitation">{'; '.join(modules['F_carbon']['limitations'])}</p>

<h2>Density &amp; Urban Context</h2>
<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Floor Area Ratio (FAR)</td><td>{modules['G_density']['far']}</td></tr>
  <tr><td>Ground Coverage</td><td>{modules['G_density']['ground_coverage_percent']}%</td></tr>
  <tr><td>Open Space</td><td>{modules['G_density']['open_space_percent']}%</td></tr>
</table>
<p class="limitation">Density metrics are calculated values, NOT regulatory compliance. {'; '.join(modules['G_density']['limitations'])}</p>

<h2>Room Summary</h2>
<p>Total Rooms: {modules['B_rooms']['summary']['total_rooms']} | Total Floor Area: {modules['B_rooms']['summary']['total_floor_area_m2']:,.0f} m² | Occupants: {modules['B_rooms']['summary']['total_occupants']}</p>

<h2>Design Optimization</h2>
<p>Baseline EPI: {modules['I_optimization']['baseline_metric_value']} kWh/m²/yr</p>
<p class="limitation">Same baseline assumptions; {'; '.join(modules['I_optimization']['limitations'])}</p>

<h2>Structural Risk Screening</h2>
<div class="disclaimer">
  <strong>⚠️ {modules['H_structural']['review_required'] and 'Professional review required' or 'Screening complete'}</strong><br>
  {modules['H_structural']['disclaimer']}
</div>
<p>Missing Information:</p>
<ul>
{''.join(f'<li>{item}</li>' for item in modules['H_structural']['missing_information'])}
</ul>

<h2>Source References</h2>
<ul>
{''.join(f'<li>{s}</li>' for s in e.source_references)}
</ul>

<footer>
  Generated by DhakaSmart Urban Density &amp; Green BIM v0.1.0<br>
  Preliminary analysis — not for construction or regulatory submission.<br>
  Confidence: {e.overall_confidence}
</footer>

</body>
</html>"""
    return html


@router.get("/projects/{project_id}/report")
def generate_report(project_id: str, format: str = "json"):
    """Generate a report for a project.

    Args:
        project_id: Project UUID.
        format: 'json', 'html', or 'csv'.

    Returns:
        JSON, HTML, or CSV report.
    """
    if project_id not in _projects:
        raise HTTPException(status_code=404, detail="Project not found.")

    project = _projects[project_id]
    rooms = _rooms.get(project_id, [])

    if not rooms:
        raise HTTPException(status_code=400, detail="No rooms for this project.")

    envelope = run_full_analysis(building=project, rooms=rooms)

    if format == "json":
        return JSONResponse(content=envelope.model_dump(mode="json"))
    elif format == "html":
        html = _generate_report_html(envelope, project, rooms)
        return HTMLResponse(content=html, status_code=200)
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'json' or 'html'.")


@router.post("/reports/preview")
def report_preview(
    building: dict,
    rooms: list[dict],
):
    """Generate a report preview from raw building + room dicts (for testing)."""
    from src.models.schemas import BuildingCreate, RoomCreate

    try:
        building_model = BuildingCreate(**building)
        room_models = [RoomCreate(**r) for r in rooms]
        envelope = run_full_analysis(building=building_model, rooms=room_models)
        html = _generate_report_html(envelope, building_model, room_models)
        return HTMLResponse(content=html, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")