export default function OptimizationPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Design Optimization</h1>
        <p className="text-slate-600 mt-2">Module I — Baseline vs alternative comparison</p>
      </header>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Baseline EPI</div>
          <div className="text-3xl font-bold text-slate-900">52.1 <span className="text-lg">kWh/m²/yr</span></div>
        </div>
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Best Alternative</div>
          <div className="text-3xl font-bold text-emerald-600">44.3 <span className="text-lg">kWh/m²/yr</span></div>
        </div>
        <div className="p-6 bg-white rounded-xl border border-slate-200">
          <div className="text-sm text-slate-500 mb-1">Improvement</div>
          <div className="text-3xl font-bold text-emerald-600">-15.0%</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Case</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">EPI (kWh/m²/yr)</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Difference</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Change</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            <tr className="bg-slate-50">
              <td className="px-6 py-4 text-sm font-medium">Baseline</td>
              <td className="px-6 py-4 text-sm">52.1</td>
              <td className="px-6 py-4 text-sm">—</td>
              <td className="px-6 py-4 text-sm">—</td>
            </tr>
            <tr>
              <td className="px-6 py-4 text-sm font-medium">Higher COP AC (4.0)</td>
              <td className="px-6 py-4 text-sm">48.2</td>
              <td className="px-6 py-4 text-sm">-3.9</td>
              <td className="px-6 py-4 text-sm text-emerald-600">-7.5%</td>
            </tr>
            <tr>
              <td className="px-6 py-4 text-sm font-medium">Double low-E glazing + overhangs</td>
              <td className="px-6 py-4 text-sm">44.3</td>
              <td className="px-6 py-4 text-sm">-7.8</td>
              <td className="px-6 py-4 text-sm text-emerald-600">-15.0%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="bg-slate-50 rounded-xl p-6 text-sm">
        <h3 className="font-semibold mb-2">⚠️ Limitations</h3>
        <ul className="list-disc list-inside text-slate-600 space-y-1">
          <li>Comparison uses preliminary estimates, not simulation</li>
          <li>Percentages are relative to baseline; absolute values may vary with weather</li>
        </ul>
      </div>
    </div>
  );
}