const rooms = [
  { name: "Living Room", ratio: 10, passes: true },
  { name: "Bedroom 1", ratio: 8, passes: true },
  { name: "Bedroom 2", ratio: 8, passes: true },
  { name: "Kitchen", ratio: 6, passes: false },
  { name: "Bathroom", ratio: 10, passes: true },
];

export default function VentilationPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Ventilation Screening</h1>
        <p className="text-slate-600 mt-2">Module C — Opening ratio, cross-ventilation potential</p>
      </header>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-emerald-50 rounded-lg text-center">
          <div className="text-3xl font-bold text-emerald-700">4/5</div>
          <div className="text-sm text-emerald-800">Rooms Passing</div>
        </div>
        <div className="p-4 bg-amber-50 rounded-lg text-center">
          <div className="text-3xl font-bold text-amber-700">1</div>
          <div className="text-sm text-amber-800">Below Minimum</div>
        </div>
        <div className="p-4 bg-slate-50 rounded-lg text-center">
          <div className="text-3xl font-bold text-slate-700">Medium</div>
          <div className="text-sm text-slate-600">Confidence</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Room</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Opening Ratio</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">BNBC 5%</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {rooms.map((room, i) => (
              <tr key={i} className="hover:bg-slate-50">
                <td className="px-6 py-4 text-sm font-medium">{room.name}</td>
                <td className="px-6 py-4 text-sm">{room.ratio}%</td>
                <td className="px-6 py-4 text-sm">{room.passes ? "✅ Pass" : "⚠️ Fail"}</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 py-1 rounded text-xs ${room.passes ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                    {room.passes ? "Adequate" : "Insufficient"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="bg-slate-50 rounded-xl p-6 text-sm">
        <h3 className="font-semibold mb-2">⚠️ Limitations</h3>
        <ul className="list-disc list-inside text-slate-600 space-y-1">
          <li>Screening only; no ACH or airflow calculation</li>
          <li>Cross-ventilation is a binary indicator, not a flow rate</li>
        </ul>
      </div>
    </div>
  );
}