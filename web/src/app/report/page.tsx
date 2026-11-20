export default function ReportPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Report Export</h1>
        <p className="text-slate-600 mt-2">Generate downloadable reports with full provenance</p>
      </header>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <a href="#" className="p-6 bg-white rounded-xl border border-slate-200 hover:border-emerald-400 transition-colors">
          <div className="text-3xl mb-2">📄</div>
          <h3 className="font-semibold">PDF Report</h3>
          <p className="text-sm text-slate-600 mt-1">Full analysis with methodology</p>
          <span className="inline-block mt-3 px-3 py-1 bg-emerald-100 text-emerald-700 text-xs rounded">Download</span>
        </a>
        <a href="#" className="p-6 bg-white rounded-xl border border-slate-200 hover:border-emerald-400 transition-colors">
          <div className="text-3xl mb-2">📊</div>
          <h3 className="font-semibold">CSV Data</h3>
          <p className="text-sm text-slate-600 mt-1">Raw calculation data</p>
          <span className="inline-block mt-3 px-3 py-1 bg-emerald-100 text-emerald-700 text-xs rounded">Download</span>
        </a>
        <a href="#" className="p-6 bg-white rounded-xl border border-slate-200 hover:border-emerald-400 transition-colors">
          <div className="text-3xl mb-2">📋</div>
          <h3 className="font-semibold">HTML Report</h3>
          <p className="text-sm text-slate-600 mt-1">Printable web report</p>
          <span className="inline-block mt-3 px-3 py-1 bg-emerald-100 text-emerald-700 text-xs rounded">Preview</span>
        </a>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        <h2 className="text-xl font-semibold mb-4">Report Contents</h2>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          {[
            "Project details",
            "Building details",
            "Room details",
            "Input summary",
            "Data sources",
            "Assumptions",
            "Rule references",
            "Analysis methods",
            "Results (all modules)",
            "Recommendations",
            "Before/after comparison",
            "Uncertainty & confidence",
            "Limitations",
            "Missing information",
            "Validation status",
            "Professional review warnings",
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="text-emerald-500">✓</span>
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
        <h3 className="font-semibold text-amber-900">⚠️ Every Report Identifies Analysis as "Preliminary"</h3>
        <p className="text-sm text-amber-800 mt-1">
          Reports include explicit preliminary analysis warnings and professional review disclaimers.
        </p>
      </div>
    </div>
  );
}