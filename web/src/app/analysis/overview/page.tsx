export default function AnalysisOverviewPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Analysis Overview</h1>
        <p className="text-slate-600 mt-2">Summary of all building performance modules</p>
      </header>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { title: "Room Analyzer", status: "✅ Complete", confidence: "Medium", value: "5 rooms", href: "/projects/1/rooms" },
          { title: "Ventilation", status: "✅ Complete", confidence: "Medium", value: "80% passing", href: "/analysis/ventilation" },
          { title: "Daylight", status: "✅ Complete", confidence: "Medium", value: "85% adequate", href: "/analysis/daylight" },
          { title: "Energy", status: "✅ Complete", confidence: "Low", value: "52.1 kWh/m²/yr", href: "/analysis/energy" },
          { title: "Carbon", status: "✅ Complete", confidence: "High", value: "87 tCO₂e/yr", href: "/analysis/carbon" },
          { title: "Density", status: "✅ Complete", confidence: "Medium", value: "FAR 2.4", href: "/analysis/density" },
          { title: "Structural", status: "⚠️ Needs Review", confidence: "Insufficient", value: "Review required", href: "/analysis/structural" },
          { title: "Optimization", status: "✅ Complete", confidence: "Medium", value: "-15% EPI", href: "/optimization" },
        ].map((item, i) => (
          <a key={i} href={item.href} className="p-6 bg-white rounded-xl border border-slate-200 hover:border-emerald-400 transition-colors block">
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-semibold text-lg">{item.title}</h3>
              <span className="text-xs px-2 py-1 bg-slate-100 rounded">{item.status}</span>
            </div>
            <div className="text-2xl font-bold text-slate-900">{item.value}</div>
            <div className="mt-2 text-xs text-slate-500">Confidence: {item.confidence}</div>
          </a>
        ))}
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
        <h3 className="font-semibold text-amber-900">⚠️ Preliminary Analysis</h3>
        <p className="text-sm text-amber-800 mt-1">
          All results are screening-level estimates. See individual module pages for limitations.
        </p>
      </div>
    </div>
  );
}