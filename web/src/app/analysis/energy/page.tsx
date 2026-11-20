export default function EnergyPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Energy Analysis</h1>
        <p className="text-slate-600 mt-2">Module E — Preliminary energy estimate (NOT simulation)</p>
      </header>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Total Electricity</div>
          <div className="text-3xl font-bold text-slate-900">125,000 <span className="text-lg">kWh/yr</span></div>
        </div>
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">EPI</div>
          <div className="text-3xl font-bold text-emerald-600">52.1 <span className="text-lg">kWh/m²/yr</span></div>
        </div>
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Confidence</div>
          <div className="text-3xl font-bold text-amber-600">Low</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        <h2 className="text-xl font-semibold mb-6">Energy Breakdown</h2>
        <div className="space-y-4">
          {[
            { label: "Cooling", value: 68000, percent: 54, color: "bg-blue-500" },
            { label: "Lighting", value: 25000, percent: 20, color: "bg-yellow-500" },
            { label: "Equipment", value: 32000, percent: 26, color: "bg-slate-500" },
          ].map((item, i) => (
            <div key={i}>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium">{item.label}</span>
                <span className="text-sm">{item.value.toLocaleString()} kWh ({item.percent}%)</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3">
                <div className={`${item.color} h-3 rounded-full`} style={{ width: `${item.percent}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
        <h3 className="font-semibold text-amber-900">⚠️ Preliminary Estimate Only</h3>
        <p className="text-sm text-amber-800 mt-1">
          Cooling estimate uses rule-of-thumb W/m², not a cooling load calculation.
          Lighting/equipment densities are screening defaults.
        </p>
      </div>
    </div>
  );
}