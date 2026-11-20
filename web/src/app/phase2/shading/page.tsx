"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Sample = {
  time: string;
  altitude_deg: number;
  azimuth_deg: number;
  sun_on_facade: boolean;
  profile_angle_deg: number;
  overhang_shaded_percent: number;
  fin_shaded_percent: number;
};

type ShadingData = {
  date: string;
  facade_orientation: string;
  sunlit_hours: number;
  peak_profile_angle_deg: number;
  required_overhang_for_peak_m: number;
  samples: Sample[];
  recommendations: string[];
  confidence: string;
  limitations: string[];
};

export default function ShadingPage() {
  const [form, setForm] = useState({
    facade_azimuth_deg: 270.0,
    window_height_m: 1.5,
    window_width_m: 2.0,
    overhang_depth_m: 0.0,
    fin_depth_m: 0.6,
    date: "2026-06-21",
    obstruction_height_m: 0,
    obstruction_distance_m: 0,
  });
  const [data, setData] = useState<ShadingData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function calc() {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API}/api/v1/phase2/shading`, {
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

  const update = (k: string, v: number | string) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Shading Analysis</h1>
        <p className="text-slate-600 mt-2">Geometric shading using solar profile angles</p>
      </header>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
          <h2 className="font-semibold">Inputs</h2>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Facade Azimuth (deg, 0=N)</label>
            <select
              value={form.facade_azimuth_deg}
              onChange={(e) => update("facade_azimuth_deg", parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
              <option value={0}>0 — North</option>
              <option value={90}>90 — East</option>
              <option value={180}>180 — South</option>
              <option value={270}>270 — West</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Design Date</label>
            <input
              type="date"
              value={form.date}
              onChange={(e) => update("date", e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Window H (m)</label>
              <input
                type="number" step="0.1" min={0.1}
                value={form.window_height_m}
                onChange={(e) => update("window_height_m", parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Window W (m)</label>
              <input
                type="number" step="0.1" min={0.1}
                value={form.window_width_m}
                onChange={(e) => update("window_width_m", parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Overhang (m)</label>
              <input
                type="number" step="0.1" min={0}
                value={form.overhang_depth_m}
                onChange={(e) => update("overhang_depth_m", parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Fin Depth (m)</label>
              <input
                type="number" step="0.1" min={0}
                value={form.fin_depth_m}
                onChange={(e) => update("fin_depth_m", parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
          </div>

          <div className="border-t pt-3">
            <h3 className="text-xs font-medium mb-2">Adjacent Building (optional)</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] text-slate-600 mb-1">Height (m)</label>
                <input
                  type="number" step="1" min={0}
                  value={form.obstruction_height_m}
                  onChange={(e) => update("obstruction_height_m", parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-600 mb-1">Distance (m)</label>
                <input
                  type="number" step="1" min={0}
                  value={form.obstruction_distance_m}
                  onChange={(e) => update("obstruction_distance_m", parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
            </div>
          </div>

          <button
            onClick={calc}
            disabled={loading}
            className="w-full px-4 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 disabled:opacity-50"
          >
            {loading ? "Analysing…" : "Analyse"}
          </button>
        </div>

        <div className="lg:col-span-2 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>
          )}

          {!data && !error && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-10 text-center text-sm text-slate-500">
              Set facade and shading geometry, then analyse.
            </div>
          )}

          {data && (
            <>
              <div className="grid grid-cols-3 gap-3">
                <div className="p-4 bg-white rounded-xl border border-slate-200">
                  <div className="text-xs text-slate-500">Facade</div>
                  <div className="text-lg font-bold text-slate-900">{data.facade_orientation}</div>
                </div>
                <div className="p-4 bg-white rounded-xl border border-slate-200">
                  <div className="text-xs text-slate-500">Sunlit Hours</div>
                  <div className="text-lg font-bold text-slate-900">{data.sunlit_hours} h</div>
                </div>
                <div className="p-4 bg-white rounded-xl border border-slate-200">
                  <div className="text-xs text-slate-500">Required Overhang</div>
                  <div className="text-lg font-bold text-violet-600">
                    {data.required_overhang_for_peak_m} m
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="font-semibold mb-3">Shading Profile (30-min)</h2>
                <div className="space-y-1 max-h-72 overflow-y-auto">
                  {data.samples.map((s) => (
                    <div
                      key={s.time}
                      className={`grid grid-cols-5 gap-2 text-[11px] px-2 py-1 rounded ${
                        s.sun_on_facade ? "bg-amber-50" : "bg-slate-50 opacity-60"
                      }`}
                    >
                      <span className="font-mono">{s.time}</span>
                      <span>{s.altitude_deg.toFixed(0)}°</span>
                      <span className="text-slate-500">{s.azimuth_deg.toFixed(0)}°</span>
                      <span>{s.profile_angle_deg.toFixed(0)}° prof</span>
                      <span className="text-right">
                        {s.overhang_shaded_percent > 0 ? `🌥 ${s.overhang_shaded_percent.toFixed(0)}%` : ""}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                <h3 className="font-semibold text-xs text-emerald-900 mb-1">Recommendations</h3>
                <ul className="list-disc list-inside text-xs text-emerald-800 space-y-1">
                  {data.recommendations.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>

              <div className="bg-slate-50 rounded-xl p-4 text-[11px] text-slate-600">
                <strong>Confidence:</strong> {data.confidence} ·{" "}
                {data.limitations[0]}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}