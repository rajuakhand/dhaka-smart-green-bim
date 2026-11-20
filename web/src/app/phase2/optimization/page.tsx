"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Candidate = { design: Record<string, number>; objective: number };

type OptData = {
  method: string;
  objective_direction: string;
  design_space_size: number;
  evaluated: number;
  rejected_by_constraints: number;
  best: Candidate | null;
  ranking: Candidate[];
  limitations: string[];
  confidence: string;
};

const SPACE: Record<string, number[]> = {
  ac_cop: [2.8, 3.1, 3.5, 4.0],
  cooling_hours: [1200, 1500, 1800, 2100],
  lighting_hours: [2000, 2500, 3000],
  equipment_hours: [2000, 2500, 3000],
};

export default function OptimizationPage() {
  const [data, setData] = useState<OptData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API}/api/v1/phase2/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          building: {
            name: "Optimisation Study",
            building_type: "Residential",
            num_floors: 6,
            floor_to_floor_height_m: 3.0,
            orientation_deg: 180.0,
          },
          rooms: [
            {
              name: "Reference Room", room_type: "Residential",
              length_m: 5, width_m: 4, height_m: 3, occupants: 2,
              window_area_m2: 4, openable_window_area_m2: 2,
            },
          ],
        }),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      setData(j.modules.optimization);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Optimisation failed");
    } finally {
      setLoading(false);
    }
  }

  const total = Object.values(SPACE).reduce((a, v) => a * v.length, 1);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Parametric Optimization</h1>
        <p className="text-slate-600 mt-2">
          Exhaustive grid search over the design space, minimising EPI
        </p>
      </header>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="font-semibold mb-3">Design Space ({total} combinations)</h2>
        <div className="grid md:grid-cols-4 gap-4">
          {Object.entries(SPACE).map(([k, vals]) => (
            <div key={k} className="p-3 bg-slate-50 rounded-lg">
              <div className="text-xs font-mono font-medium text-slate-700 mb-1">{k}</div>
              <div className="flex flex-wrap gap-1">
                {vals.map((v) => (
                  <span key={v} className="px-1.5 py-0.5 bg-white border border-slate-200 rounded text-[10px] font-mono">
                    {v}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        <button
          onClick={run}
          disabled={loading}
          className="mt-4 px-6 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 disabled:opacity-50"
        >
          {loading ? "Searching…" : "Run Grid Search"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
      )}

      {!data && !error && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-10 text-center text-sm text-slate-500">
          Run the grid search to evaluate every design combination.
        </div>
      )}

      {data && data.best && (
        <>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
              <div className="text-xs text-emerald-700">Best EPI</div>
              <div className="text-3xl font-bold text-emerald-800">{data.best.objective}</div>
              <div className="text-[11px] text-emerald-700">kWh/m²/yr</div>
            </div>
            <div className="p-4 bg-white rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500">Combinations Evaluated</div>
              <div className="text-3xl font-bold text-slate-900">{data.evaluated}</div>
            </div>
            <div className="p-4 bg-white rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500">Search Direction</div>
              <div className="text-3xl font-bold text-slate-900">{data.objective_direction}</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="font-semibold mb-3">Top 10 Designs</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-3 py-2 font-semibold text-slate-700">#</th>
                    {Object.keys(SPACE).map((k) => (
                      <th key={k} className="text-left px-3 py-2 font-semibold text-slate-700">{k}</th>
                    ))}
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">EPI</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.ranking.slice(0, 10).map((row, i) => (
                    <tr key={i} className={i === 0 ? "bg-emerald-50" : "hover:bg-slate-50"}>
                      <td className="px-3 py-2 font-mono text-slate-500">{i + 1}</td>
                      {Object.keys(SPACE).map((k) => (
                        <td key={k} className="px-3 py-2 font-mono">{row.design[k]}</td>
                      ))}
                      <td className="px-3 py-2 text-right font-mono font-bold">{row.objective}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-xs text-slate-500 mb-1">Optimal configuration</div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.best.design).map(([k, v]) => (
                <span key={k} className="px-2 py-1 bg-violet-50 text-violet-700 text-xs rounded font-mono">
                  {k}={v}
                </span>
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
  );
}