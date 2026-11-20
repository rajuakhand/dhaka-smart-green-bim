"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type MonthRow = {
  name: string;
  tmean_c: number | null;
  extreme_max_c: number | null;
  extreme_min_c: number | null;
  ghi_kwh_m2_day: number | null;
};

type ClimateData = {
  dataset: {
    dataset_id: string;
    source_name: string;
    period: string;
    resolution: string;
    verification_status: string;
    annual_mean_temp_c: number | null;
    extreme_max_temp_c: number | null;
    extreme_min_temp_c: number | null;
    annual_mean_ghi_kwh_m2_day: number | null;
    months: Record<string, MonthRow>;
    engineering_notes: string[];
    limitations: string[];
  };
  cooling_degree_days: { available: boolean; cdd_total: number | null; method: string };
  engineering_note: string;
};

export default function ClimatePage() {
  const [data, setData] = useState<ClimateData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lat, setLat] = useState(23.8103);
  const [lon, setLon] = useState(90.4125);

  async function load() {
    setError(null);
    try {
      const r = await fetch(
        `${API}/api/v1/phase2/climate?latitude=${lat}&longitude=${lon}`
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setData(await r.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load climate data");
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Climate Data</h1>
        <p className="text-slate-600 mt-2">
          NASA POWER satellite-derived monthly normals with BMD fallback
        </p>
      </header>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Latitude</label>
            <input
              type="number"
              step="0.0001"
              value={lat}
              onChange={(e) => setLat(parseFloat(e.target.value) || 0)}
              className="w-40 px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Longitude</label>
            <input
              type="number"
              step="0.0001"
              value={lon}
              onChange={(e) => setLon(parseFloat(e.target.value) || 0)}
              className="w-40 px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>
          <button
            onClick={load}
            className="px-5 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700"
          >
            Load
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {data && (
        <>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { label: "Dataset", value: data.dataset.dataset_id, sub: data.dataset.period },
              { label: "Mean Temp", value: `${data.dataset.annual_mean_temp_c} °C`, sub: "from T2M" },
              { label: "Extreme Max", value: `${data.dataset.extreme_max_temp_c} °C`, sub: "design condition" },
              { label: "Mean GHI", value: `${data.dataset.annual_mean_ghi_kwh_m2_day}`, sub: "kWh/m²/day" },
            ].map((s) => (
              <div key={s.label} className="p-4 bg-white rounded-xl border border-slate-200">
                <div className="text-xs text-slate-500">{s.label}</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">{s.value}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">{s.sub}</div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="font-semibold mb-1">{data.dataset.source_name}</h2>
            <div className="flex gap-3 text-xs text-slate-500 mb-4">
              <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded">
                {data.dataset.verification_status}
              </span>
              <span>Resolution: {data.dataset.resolution}</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-3 py-2 font-semibold text-slate-700">Month</th>
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">Mean °C</th>
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">Extreme Max °C</th>
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">GHI kWh/m²/day</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {Object.entries(data.dataset.months).map(([m, row]) => (
                    <tr key={m} className="hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium">{row.name}</td>
                      <td className="px-3 py-2 text-right font-mono">{row.tmean_c?.toFixed(1) ?? "—"}</td>
                      <td className="px-3 py-2 text-right font-mono">{row.extreme_max_c?.toFixed(1) ?? "—"}</td>
                      <td className="px-3 py-2 text-right font-mono">{row.ghi_kwh_m2_day?.toFixed(2) ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 p-3 bg-slate-50 rounded-lg text-xs text-slate-600">
              <strong>Cooling Degree Days (base 26 °C):</strong>{" "}
              {data.cooling_degree_days.cdd_total?.toLocaleString() ?? "n/a"}
            </div>

            <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
              <strong>Engineering note:</strong> {data.engineering_note}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="font-semibold text-sm mb-2">Limitations</h3>
            <ul className="list-disc list-inside text-xs text-slate-600 space-y-1">
              {data.dataset.limitations.map((l, i) => (
                <li key={i}>{l}</li>
              ))}
              {data.dataset.engineering_notes.map((l, i) => (
                <li key={`n${i}`} className="text-amber-700">{l}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}