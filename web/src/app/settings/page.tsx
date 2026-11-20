export default function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Project Settings</h1>
        <p className="text-slate-600 mt-2">Configure project preferences and data sources</p>
      </header>

      <div className="bg-white rounded-xl border border-slate-200 p-8 space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-4">Emission Factor Source</h2>
          <div className="space-y-2">
            {[
              { id: "DoE-GEF", name: "DoE Grid Emission Factor (Recommended)", value: "0.62 kg CO₂e/kWh, 2019-22, Verified" },
              { id: "Ember-OWID", name: "Ember/OWID", value: "0.696 kg CO₂e/kWh, 2025, Verified" },
              { id: "User-supplied", name: "User-supplied", value: "Custom value, unverified" },
            ].map((option) => (
              <label key={option.id} className="flex items-center gap-3 p-4 border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-50">
                <input type="radio" name="emission-factor" value={option.id} defaultChecked={option.id === "DoE-GEF"} className="text-emerald-600" />
                <div>
                  <div className="font-medium text-sm">{option.name}</div>
                  <div className="text-xs text-slate-500">{option.value}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-4">Analysis Defaults</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">AC COP</label>
              <input type="number" step="0.1" value="3.1" className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Cooling Hours/Year</label>
              <input type="number" value="1800" className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Lighting Hours/Year</label>
              <input type="number" value="2500" className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Equipment Hours/Year</label>
              <input type="number" value="2500" className="w-full px-4 py-2 border border-slate-300 rounded-lg" />
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold mb-4">Display Preferences</h2>
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="text-emerald-600" />
              <span className="text-sm">Show confidence levels on all results</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="text-emerald-600" />
              <span className="text-sm">Show source references</span>
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" defaultChecked className="text-emerald-600" />
              <span className="text-sm">Show limitations on reports</span>
            </label>
          </div>
        </div>

        <div className="flex justify-end pt-6 border-t border-slate-200">
          <button className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700">
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}