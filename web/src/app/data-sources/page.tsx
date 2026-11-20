const sources = [
  { id: "SRC-001", name: "BNBC 2020", type: "Regulatory", status: "✅ Verified", desc: "Occupancy, ventilation, daylight, energy" },
  { id: "SRC-002", name: "RAJUK DAP 2022-2035", type: "Regulatory", status: "✅ Verified", desc: "FAR, coverage, open space" },
  { id: "SRC-006", name: "DoE Grid Emission Factor", type: "Emission", status: "✅ Verified", desc: "0.61-0.62 tCO₂/MWh" },
  { id: "SRC-008", name: "Ember/OWID", type: "Emission", status: "✅ Verified", desc: "0.696 kg CO₂e/kWh" },
  { id: "SRC-010", name: "EnergyPlus EPW", type: "Climate", status: "✅ Verified", desc: "Dhaka TMYx" },
  { id: "SRC-011", name: "NASA POWER", type: "Climate", status: "✅ Verified", desc: "Hourly solar, met" },
];

export default function DataSourcesPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Data Sources</h1>
        <p className="text-slate-600 mt-2">All sources are verified with traceable provenance</p>
      </header>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">ID</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Source</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Type</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Status</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {sources.map((source) => (
              <tr key={source.id} className="hover:bg-slate-50">
                <td className="px-6 py-4 text-sm font-mono text-slate-600">{source.id}</td>
                <td className="px-6 py-4 text-sm font-medium">{source.name}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{source.type}</td>
                <td className="px-6 py-4 text-sm">{source.status}</td>
                <td className="px-6 py-4 text-sm text-slate-600">{source.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
        <h3 className="font-semibold text-emerald-900">Source Governance</h3>
        <p className="text-sm text-emerald-800 mt-2">
          Each dataset contains: Dataset ID, source name, source URL, publisher, data type,
          geographic coverage, time period, date accessed, version, units, license, and quality status.
        </p>
      </div>
    </div>
  );
}