export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-600 mt-2">Overview of your building performance projects</p>
      </header>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-lg mb-2">Quick Stats</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-slate-600">Projects</span><span className="font-mono font-semibold">--</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Rooms</span><span className="font-mono font-semibold">--</span></div>
            <div className="flex justify-between"><span className="text-slate-600">Avg EPI</span><span className="font-mono font-semibold">-- kWh/m²/yr</span></div>
          </div>
        </div>

        <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-lg mb-2">Quick Actions</h3>
          <div className="space-y-3">
            <a href="/projects/new" className="block px-4 py-2 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-medium hover:bg-emerald-100 text-center">
              + Create New Project
            </a>
            <a href="/dashboard" className="block px-4 py-2 bg-slate-50 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-100 text-center">
              View All Projects
            </a>
          </div>
        </div>

        <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
          <h3 className="font-semibold text-lg mb-2">System Status</h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2"><span className="w-2 h-2 bg-emerald-500 rounded-full"></span><span>API: Online</span></div>
            <div className="flex items-center gap-2"><span className="w-2 h-2 bg-emerald-500 rounded-full"></span><span>Database: Connected</span></div>
            <div className="flex items-center gap-2"><span className="w-2 h-2 bg-emerald-500 rounded-full"></span><span>EPW: Available</span></div>
          </div>
        </div>
      </div>

      <div className="p-6 bg-amber-50 border border-amber-200 rounded-xl">
        <h3 className="font-semibold text-amber-900">⚠️ Preliminary Analysis</h3>
        <p className="text-sm text-amber-800 mt-1">
          All calculations are screening-level estimates. Results require professional verification.
        </p>
      </div>
    </div>
  );
}