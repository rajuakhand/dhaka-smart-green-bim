export default function CarbonPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Carbon Analysis</h1>
        <p className="text-slate-600 mt-2">Module F — Operational electricity emissions</p>
      </header>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Electricity</div>
          <div className="text-3xl font-bold text-slate-900">125,000 <span className="text-lg">kWh/yr</span></div>
        </div>
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Emission Factor</div>
          <div className="text-3xl font-bold text-slate-900">0.62 <span className="text-lg">kg/kWh</span></div>
          <div className="text-xs text-slate-500 mt-1">DoE GEF 2019-22</div>
        </div>
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Confidence</div>
          <div className="text-3xl font-bold text-emerald-600">High</div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-8">
          <h2 className="text-xl font-semibold mb-4">Operational Emissions</h2>
          <div className="text-4xl font-bold text-slate-900 mb-2">77.5 <span className="text-lg">tCO₂e/yr</span></div>
          <p className="text-slate-600 text-sm">125,000 kWh × 0.62 kg CO₂e/kWh</p>
          <div className="mt-4 p-3 bg-slate-50 rounded text-sm">
            <span className="font-medium">Scope:</span> Location-based (Scope 2)
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-8">
          <h2 className="text-xl font-semibold mb-4">Source Details</h2>
          <div className="space-y-2 text-sm">
            <div><span className="text-slate-600">Source:</span> DoE Grid Emission Factor</div>
            <div><span className="text-slate-600">Year:</span> 2019-2022</div>
            <div><span className="text-slate-600">Boundary:</span> Location-based</div>
            <div><span className="text-slate-600">Status:</span> ✅ Verified</div>
          </div>
        </div>
      </div>

      <div className="bg-slate-50 rounded-xl p-6 text-sm">
        <h3 className="font-semibold mb-2">⚠️ Limitations</h3>
        <ul className="list-disc list-inside text-slate-600 space-y-1">
          <li>Only operational electricity emissions; no embodied, transport, or end-of-life</li>
          <li>Grid emission factor is annual average; marginal emissions not considered</li>
          <li>Embodied carbon: Not calculated (no verified Bangladesh EPDs available)</li>
        </ul>
      </div>
    </div>
  );
}