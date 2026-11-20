"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type SensRow = {
  parameter: string;
  baseline_value: number;
  percent_swing_of_baseline: number;
  elasticity: number;
  interpretation: string;
};

type SensData = {
  baseline_metric: number;
  delta_percent: number;
  results: SensRow[];
  ranking_by_influence: string[];
  most_influential: string;
  least_influential: string;
  limitations: string[];
};

export default function SensitivityPage() {
  const [form, setForm] = useState({
    ac_cop: 3.1,
    cooling_hours: 1800,
    lighting_hours: 2500,
    equipment_hours: 2500,
    delta: 0.1,
  });
  const [data, setData] = useState<SensData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function calc() {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API}/api/v1/phase2/sensitivity`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      setData(j);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Calculation failed");
    } finally {
      setLoading(false);
    }
  }

  const update = (k: string, v: number) => setForm((f) => ({ ...f, [k]: v }));
  const maxSwing = data ? Math.max(...data.results.map((r) => r.percent_swing_of_baseline), 1) : 1;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Sensitivity Analysis</h1>
        <p className="text-slate-600 mt-2">
          One-at-a-time perturbation to find which inputs drive the result
        </p>
      </header>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
          <h2 className="font-semibold">Baseline Assumptions</h2>
          {[
            ["AC COP", "ac_cop", 1.5, 8],
            ["Cooling Hours/yr", "cooling_hours", 0, 8760],
            ["Lighting Hours/yr", "lighting_hours", 0, 8760],
            ["Equipment Hours/yr", "equipment_hours", 0, 8760],
          ].map(([label, key, min, max]) => (
            <div key={key as string}>
              <label className="block text-xs font-medium text-slate-600 mb-1">{label as string}</label>
              <input
                type="number" step={0.1} min={min as number} max={max as number}
                value={form[key as keyof typeof form] as number}
                onChange={(e) => update(key as string, parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
          ))}
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Perturbation (±%)</label>
            <input
              type="number" step="5" min={1} max={100}
              value={Math.round(form.delta * 100)}
              onChange={(e) => update("delta", (parseFloat(e.target.value) || 10) / 100)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>
          <button
            onClick={calc}
            disabled={loading}
            className="w-full px-4 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 disabled:opacity-50"
          >
            {loading ? "Running…" : "Run Sensitivity"}
          </button>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
          )}

          {!data && !error && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-10 text-center text-sm text-slate-500">
              Set baseline assumptions, then run.
            </div>
          )}

          {data && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-white rounded-xl border border-slate-200">
                  <div className="text-xs text-slate-500">Baseline Electricity</div>
                  <div className="text-2xl font-bold text-slate-900">
                    {data.baseline_metric.toLocaleString()} kWh/yr
                  </div>
                </div>
                <div className="p-4 bg-white rounded-xl border border-violet-200">
                  <div className="text-xs text-slate-500">Most Influential Input</div>
                  <div className="text-2xl font-bold text-violet-600">
                    {data.most_influential}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    least: {data.least_influential}
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="font-semibold mb-4">Parameter Influence (ranked)</h2>
                <div className="space-y-4">
                  {[...data.results]
                    .sort((a, b) => b.percent_swing_of_baseline - a.percent_swing_of_baseline)
                    .map((r) => (
                      <div key={r.parameter}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="font-mono font-medium">{r.parameter}</span>
                          <span className="text-slate-600">
                            {r.percent_swing_of_baseline.toFixed(2)}% swing ·{" "}
                            <span className={r.elasticity < 0 ? "text-blue-600" : "text-amber-600"}>
                              elasticity {r.elasticity.toFixed(3)}
                            </span>
                          </span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2.5">
                          <div
                            className="h-2.5 rounded-full bg-violet-500"
                            style={{ width: `${(r.percent_swing_of_baseline / maxSwing) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <h3 className="font-semibold text-xs text-amber-900 mb-1">Limitations</h3>
                <ul className="list-disc list-inside text-[11px] text-amber-800 space-y-0.5">
                  {data.limitations.map((l, i) => <li key={i}>{l}</li>)}
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}