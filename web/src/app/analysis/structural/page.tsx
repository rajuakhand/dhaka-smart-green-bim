export default function StructuralPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Structural Risk Screening</h1>
        <p className="text-slate-600 mt-2">Module H — Missing info flags, professional review reminders</p>
      </header>

      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <h3 className="font-semibold text-red-900">⚠️ Professional Review Required</h3>
        <p className="text-sm text-red-800 mt-1">
          This is NOT a structural assessment. Requires a qualified structural engineer for any safety determination.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-8">
          <h2 className="text-xl font-semibold mb-4">Missing Information</h2>
          <ul className="space-y-3">
            {[
              "Structural drawings not provided",
              "Material strength (concrete grade) not specified",
              "Foundation type and details not provided",
              "Soil investigation / geotechnical report not available",
              "Seismic zone verification per BNBC not confirmed",
            ].map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="text-red-500 mt-0.5">●</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-8">
          <h2 className="text-xl font-semibold mb-4">Review Flags</h2>
          <div className="space-y-4">
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="font-medium text-sm">Height Review</div>
              <div className="text-xs text-slate-600 mt-1">Building has 6 floors (greater than 6): seismic design per BNBC Part 6 required.</div>
            </div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <div className="font-medium text-sm">Age Review</div>
              <div className="text-xs text-slate-600 mt-1">Construction year: 2020 (no age flag)</div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-50 rounded-xl p-6 text-sm">
        <h3 className="font-semibold mb-2">What This Module Does</h3>
        <p className="text-slate-600">
          Collects relevant information and produces review flags and missing-information lists.
          It never claims structural safety. All conclusions require qualified professional review.
        </p>
      </div>
    </div>
  );
}