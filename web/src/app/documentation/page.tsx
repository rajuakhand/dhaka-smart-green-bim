const sections = [
  {
    title: "Engineering Principles",
    items: [
      "No fabricated data — every rule has a traceable source",
      "Deterministic calculations — testable and documented",
      "AI assists, never replaces engineering calculation logic",
      "Uncertainty always shown — every result carries confidence",
      "Preliminary = preliminary — no pass/fail without simulation",
      "Professional review required — structural safety needs qualified engineer",
    ],
  },
  {
    title: "Data Sources",
    items: [
      "BNBC 2020 (Occupancy, Ventilation, Daylight, Energy)",
      "RAJUK DAP 2022-2035 (FAR, coverage, open space)",
      "DoE Grid Emission Factor 2019-22 (0.61-0.62 tCO₂/MWh)",
      "Ember/OWID (0.696 kg CO₂e/kWh, CC BY 4.0)",
      "EnergyPlus EPW (Dhaka SWERA 419230)",
      "NASA POWER (Hourly solar, met, 0.5° grid)",
      "SREDA BEEER Guideline v2 (Rating criteria)",
      "World Bank BEEER Survey (Residential EPI ~42 kWh/m²/yr)",
    ],
  },
  {
    title: "Calculation Methods",
    items: [
      "Ventilation: Opening ratio = openable area / floor area × 100",
      "Daylight: WWR = window area / wall area × 100",
      "Energy: Cooling = (AC capacity × area × hours) / COP / 1000",
      "Carbon: Emissions = electricity × grid emission factor",
      "Density: FAR = total floor area / plot area",
    ],
  },
  {
    title: "Limitations",
    items: [
      "Screening only; no ACH, sDA, or ASE simulation",
      "Cooling estimate uses rule-of-thumb W/m², not load calculation",
      "Embodied carbon: Not calculated (no verified Bangladesh EPDs)",
      "Grid emission factor is annual average; marginal not considered",
      "RAJUK DAP zone limits require manual lookup; not GIS-verified",
    ],
  },
];

export default function DocumentationPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Documentation &amp; Methodology</h1>
        <p className="text-slate-600 mt-2">How every number on this platform is produced</p>
      </header>

      {sections.map((section, i) => (
        <div key={i} className="bg-white rounded-xl border border-slate-200 p-8">
          <h2 className="text-xl font-semibold mb-4">{section.title}</h2>
          <ul className="space-y-2">
            {section.items.map((item, j) => (
              <li key={j} className="flex items-start gap-2 text-sm">
                <span className="text-emerald-500 mt-0.5">•</span>
                <span className="text-slate-700">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      ))}

      <div className="bg-slate-900 text-white rounded-xl p-8">
        <h2 className="text-xl font-semibold mb-4">Source Registry</h2>
        <p className="text-sm text-slate-300 mb-4">
          Each dataset contains: Dataset ID, source name, source URL, publisher, data type,
          geographic coverage, time period, date accessed, version, units, license, and quality status.
        </p>
        <a href="/data-sources" className="inline-block px-4 py-2 bg-emerald-600 rounded-lg text-sm font-medium hover:bg-emerald-700">
          View Data Sources
        </a>
      </div>
    </div>
  );
}