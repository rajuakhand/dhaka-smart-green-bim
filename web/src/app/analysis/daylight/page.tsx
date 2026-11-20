const rooms = [
  { name: "Living Room", wwr: 10, passes: true, potential: "Adequate" },
  { name: "Bedroom 1", wwr: 8, passes: false, potential: "Marginal" },
  { name: "Bedroom 2", wwr: 8, passes: false, potential: "Marginal" },
  { name: "Kitchen", wwr: 6, passes: false, potential: "Insufficient" },
  { name: "Bathroom", wwr: 10, passes: true, potential: "Adequate" },
];

export default function DaylightPage() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Daylight Screening</h1>
        <p className="text-slate-600 mt-2">Module D — Glazing ratio, obstruction, shading assessment</p>
      </header>

      <div className="grid md:grid-cols-3 gap-4 mb-6">
        <div className="p-4 bg-emerald-50 rounded-lg text-center">
          <div className="text-3xl font-bold text-emerald-700">2/5</div>
          <div className="text-sm text-emerald-800">Above 10%</div>
        </div>
        <div className="p-4 bg-amber-50 rounded-lg text-center">
          <div className="text-3xl font-bold text-amber-700">2</div>
          <div className="text-sm text-amber-800">Marginal</div>
        </div>
        <div className="p-4 bg-slate-50 rounded-lg text-center">
          <div className="text-3xl font-bold text-slate-700">Low</div>
          <div className="text-sm text-slate-600">Confidence</div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Room</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">WWR</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">BNBC 10%</th>
              <th className="text-left px-6 py-3 text-sm font-semibold text-slate-700">Potential</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {rooms.map((room, i) => (
              <tr key={i} className="hover:bg-slate-50">
                <td className="px-6 py-4 text-sm font-medium">{room.name}</td>
                <td className="px-6 py-4 text-sm">{room.wwr}%</td>
                <td className="px-6 py-4 text-sm">{room.passes ? "✅ Pass" : "⚠️ Below"}</td>
                <td className="px-6 py-4 text-sm">
                  <span className={`px-2 py-1 rounded text-xs ${
                    room.potential === "Adequate" ? "bg-emerald-100 text-emerald-700" :
                    room.potential === "Marginal" ? "bg-amber-100 text-amber-700" :
                    "bg-red-100 text-red-700"
                  }`}>
                    {room.potential}
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
          <li>Screening only; no lux, DF, sDA, or ASE simulation</li>
          <li>WWR screening does not account for room orientation or external geometry</li>
        </ul>
      </div>
    </div>
  );
}