export default function DensityPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Density &amp; Urban Context</h1>
        <p className="text-slate-600 mt-2">Module G — FAR, ground coverage, open space, RAJUK DAP</p>
      </header>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">FAR</div>
          <div className="text-3xl font-bold text-slate-900">2.4</div>
        </div>
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Ground Coverage</div>
          <div className="text-3xl font-bold text-slate-900">50%</div>
        </div>
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Open Space</div>
          <div className="text-3xl font-bold text-slate-900">50%</div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-8">
          <h2 className="text-xl font-semibold mb-4">Calculation Details</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-slate-600">Total Floor Area</span><span className="font-mono">1,200 m²</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Plot Area</span><span className="font-mono">500 m²</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Footprint</span><span className="font-mono">250 m²</span></div>
            <div className="flex justify-between border-t pt-3"><span className="font-medium">FAR</span><span className="font-mono font-bold">2.4</span></div>
            <div className="flex justify-between"><span className="font-medium">Coverage</span><span className="font-mono font-bold">50%</span></div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-8">
          <h2 className="text-xl font-semibold mb-4">RAJUK DAP Reference</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between"><span className="text-slate-600">Zone</span><span className="font-medium">Mirpur</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Max FAR</span><span className="font-mono">3.4</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Max Coverage</span><span className="font-mono">65%</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Min Open Space</span><span className="font-mono">35%</span></div>
          </div>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 text-sm">
        <h3 className="font-semibold text-amber-900">⚠️ Density Metrics are NOT Compliance Claims</h3>
        <p className="text-amber-800 mt-1">
          These are calculated values, not regulatory compliance. RAJUK DAP zone limits require manual lookup; not GIS-verified.
        </p>
      </div>
    </div>
  );
}