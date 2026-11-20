export default function FloorPlanPage() {
  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Floor Plan</h1>
        <p className="text-slate-600 mt-2">Visual representation of building layout</p>
      </header>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        <h2 className="text-xl font-semibold mb-6">Building Layout — Floor 1</h2>
        <div className="border-2 border-slate-300 bg-slate-50 rounded-lg p-8 relative" style={{ minHeight: "500px" }}>
          <div className="grid grid-cols-3 gap-4 h-full">
            <div className="bg-white border-2 border-emerald-500 rounded-lg p-4 flex items-center justify-center">
              <span className="font-medium text-slate-700">Living Room</span>
            </div>
            <div className="bg-white border-2 border-emerald-500 rounded-lg p-4 flex items-center justify-center">
              <span className="font-medium text-slate-700">Bedroom 1</span>
            </div>
            <div className="bg-white border-2 border-emerald-500 rounded-lg p-4 flex items-center justify-center">
              <span className="font-medium text-slate-700">Bedroom 2</span>
            </div>
            <div className="bg-white border-2 border-emerald-500 rounded-lg p-4 flex items-center justify-center">
              <span className="font-medium text-slate-700">Kitchen</span>
            </div>
            <div className="bg-white border-2 border-emerald-500 rounded-lg p-4 flex items-center justify-center">
              <span className="font-medium text-slate-700">Bathroom</span>
            </div>
            <div className="bg-white border-2 border-slate-300 rounded-lg p-4 flex items-center justify-center">
              <span className="font-medium text-slate-500">Corridor</span>
            </div>
          </div>
          <div className="absolute top-2 left-2 px-2 py-1 bg-white border border-slate-200 rounded text-xs">
            North ↑
          </div>
        </div>
        <div className="mt-4 flex gap-4 text-sm">
          <span className="flex items-center gap-2"><span className="w-3 h-3 bg-emerald-500 rounded"></span>Room</span>
          <span className="flex items-center gap-2"><span className="w-3 h-3 bg-slate-300 rounded"></span>Other</span>
        </div>
      </div>
    </div>
  );
}