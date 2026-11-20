"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type DfResult = {
  daylight_factor: {
    daylight_factor_percent: number;
    interpretation: string;
    method: string;
    confidence: string;
    limitations: string[];
    inputs: { visible_sky_angle_rad: number; internal_surface_area_m2: number };
  };
  indicative_lux: { indicative_interior_illuminance_lux: number; design_sky_illuminance_lux: number };
};

export default function DaylightPage() {
  const [form, setForm] = useState({
    window_area_m2: 3.0,
    window_width_m: 2.0,
    window_height_m: 1.5,
    room_length_m: 5.0,
    room_width_m: 4.0,
    room_height_m: 3.0,
    glazing_type: "Clear",
    obstruction_height_m: 0,
    obstruction_distance_m: 0,
  });
  const [result, setResult] = useState<DfResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function calc() {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${API}/api/v1/phase2/daylight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      setResult(j);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Calculation failed");
    } finally {
      setLoading(false);
    }
  }

  const update = (k: string, v: number | string) =>
    setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Daylight Factor</h1>
        <p className="text-slate-600 mt-2">
          CIBSE / BRE average daylight factor (CIE overcast sky)
        </p>
      </header>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 space-y-4">
          <h2 className="font-semibold">Room &amp; Window Inputs</h2>

          <div className="grid grid-cols-2 gap-3">
            {[
              ["Room Length (m)", "room_length_m", 0.1, 50],
              ["Room Width (m)", "room_width_m", 0.1, 50],
              ["Room Height (m)", "room_height_m", 0.1, 15],
              ["Window Area (m²)", "window_area_m2", 0.1, 100],
              ["Window Width (m)", "window_width_m", 0.1, 20],
              ["Window Height (m)", "window_height_m", 0.1, 10],
            ].map(([label, key, min, max]) => (
              <div key={key as string}>
                <label className="block text-xs font-medium text-slate-600 mb-1">{label as string}</label>
                <input
                  type="number"
                  step={min}
                  min={min}
                  max={max}
                  value={form[key as keyof typeof form] as number}
                  onChange={(e) => update(key as string, parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
            ))}
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Glazing Type</label>
            <select
              value={form.glazing_type}
              onChange={(e) => update("glazing_type", e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
              <option>Clear</option>
              <option>Tinted</option>
              <option>Double low-E</option>
              <option>Other</option>
            </select>
          </div>

          <div className="border-t pt-4">
            <h3 className="text-sm font-medium mb-2">External Obstruction (optional)</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Height (m)</label>
                <input
                  type="number"
                  min={0}
                  step={0.5}
                  value={form.obstruction_height_m}
                  onChange={(e) => update("obstruction_height_m", parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-600 mb-1">Distance (m)</label>
                <input
                  type="number"
                  min={0}
                  step={0.5}
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
            className="w-full px-5 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-700 disabled:opacity-50"
          >
            {loading ? "Calculating…" : "Calculate Daylight Factor"}
          </button>
        </div>

        <div className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {!result && !error && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-8 text-center text-sm text-slate-500">
              Enter room and window dimensions, then calculate.
            </div>
          )}

          {result && (
            <>
              <div className="bg-white rounded-xl border border-slate-200 p-6 text-center">
                <div className="text-xs uppercase tracking-wide text-slate-500">Daylight Factor</div>
                <div className="text-5xl font-bold text-violet-600 mt-1">
                  {result.daylight_factor.daylight_factor_percent}
                  <span className="text-xl">%</span>
                </div>
                <div className="inline-block mt-2 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700">
                  {result.daylight_factor.interpretation}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-white rounded-xl border border-slate-200">
                  <div className="text-xs text-slate-500">Indicative Interior Illuminance</div>
                  <div className="text-2xl font-bold text-slate-900">
                    {result.indicative_lux.indicative_interior_illuminance_lux} lux
                  </div>
                  <div className="text-[11px] text-slate-400">
                    at {result.indicative_lux.design_sky_illuminance_lux.toLocaleString()} lux sky
                  </div>
                </div>
                <div className="p-4 bg-white rounded-xl border border-slate-200">
                  <div className="text-xs text-slate-500">Confidence</div>
                  <div className="text-2xl font-bold text-amber-600">
                    {result.daylight_factor.confidence.replace(" confidence", "")}
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h3 className="font-semibold text-sm mb-2">Method</h3>
                <p className="text-xs text-slate-600 mb-3">{result.daylight_factor.method}</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Visible sky angle</span>
                    <span className="font-mono">{result.daylight_factor.inputs.visible_sky_angle_rad} rad</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Internal area</span>
                    <span className="font-mono">{result.daylight_factor.inputs.internal_surface_area_m2} m²</span>
                  </div>
                </div>
              </div>

              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <h3 className="font-semibold text-xs text-amber-900 mb-1">Limitations</h3>
                <ul className="list-disc list-inside text-[11px] text-amber-800 space-y-0.5">
                  {result.daylight_factor.limitations.map((l, i) => (
                    <li key={i}>{l}</li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}