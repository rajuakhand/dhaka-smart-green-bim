"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Facade = { azimuth_deg: number; compass: string; daily_poa_kwh_m2: number; peak_poa_w_m2: number };
type SolarData = {
  sun_path: { daylight_hours: number; peak_altitude_deg: number; peak_time: string; samples: { time: string; altitude_deg: number; azimuth_deg: number; compass: string }[] };
  facade_solar: { facades: Record<string, Facade>; highest_exposure_facade: string; lowest_exposure_facade: string; date: string };
};

export default function SolarPage() {
  const [data, setData] = useState<SolarData | null>(null);
  const [date, setDate] = useState("2026-06-21");
  const [orientation, setOrientation] = useState(180.0);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const r = await fetch(`${API}/api/v1/phase2/solar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latitude: 23.8103, longitude: 90.4125, orientation_deg: orientation, date }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setData(await r.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  // simple sun-path chart via SVG
  function sunPathChart(samples: SolarData["sun_path"]["samples"]) {
    const w = 700, h = 220, pad = 30;
    const pts = samples.map((s) => ({
      x: pad + (parseInt(s.time.slice(0, 2)) + parseInt(s.time.slice(3)) / 60) / 24 * (w - 2 * pad),
      y: h - pad - (Math.max(s.altitude_deg, 0) / 90) * (h - 2 * pad),
      alt: s.altitude_deg,
      t: s.time,
    }));
    const path = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
    return (
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full">
        <line x1={pad} y1={h - pad} x2={w - pad} y2={h - pad} stroke="#cbd5e1" strokeWidth="1" />
        <line x1={pad} y1={pad} x2={pad} y2={h - pad} stroke="#cbd5e1" strokeWidth="1" />
        <path d={path} fill="none" stroke="#f59e0b" strokeWidth="2.5" />
        {pts.filter((_, i) => i % 4 === 0).map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="2.5" fill="#f59e0b" opacity={p.alt > 0 ? 1 : 0.3} />
        ))}
        <text x={pad} y={pad - 8} fontSize="10" fill="#64748b">Altitude (deg)</text>
        <text x={w - pad} y={h - 8} fontSize="10" fill="#64748b" textAnchor="end">24 h</text>
      </svg>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Solar Geometry</h1>
        <p className="text-slate-600 mt-2">
          NREL SPA solar position + Ineichen-Perez clear-sky irradiance (pvlib)
        </p>
      </header>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Design Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Orientation (deg, 0=N)</label>
            <input
              type="number"
              min={0}
              max={360}
              value={orientation}
              onChange={(e) => setOrientation(parseFloat(e.target.value) || 0)}
              className="w-36 px-3 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>
          <button
            onClick={load}
            disabled={loading}
            className="px-5 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 disabled:opacity-50"
          >
            {loading ? "Calculating…" : "Calculate"}
          </button>
          {[
            ["Summer solstice", "2026-06-21"],
            ["Equinox", "2026-03-20"],
            ["Winter solstice", "2026-12-21"],
          ].map(([label, d]) => (
            <button
              key={d}
              onClick={() => { setDate(d); }}
              className="px-3 py-2 border border-slate-300 rounded-lg text-xs hover:bg-slate-50"
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {data && (
        <>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="p-4 bg-white rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500">Daylight Duration</div>
              <div className="text-3xl font-bold text-slate-900">{data.sun_path.daylight_hours} h</div>
            </div>
            <div className="p-4 bg-white rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500">Peak Solar Altitude</div>
              <div className="text-3xl font-bold text-amber-600">{data.sun_path.peak_altitude_deg}°</div>
              <div className="text-[11px] text-slate-400">at {data.sun_path.peak_time}</div>
            </div>
            <div className="p-4 bg-white rounded-xl border border-slate-200">
              <div className="text-xs text-slate-500">Most Exposed Facade</div>
              <div className="text-3xl font-bold text-slate-900">{data.facade_solar.highest_exposure_facade}</div>
              <div className="text-[11px] text-slate-400">highest daily POA</div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="font-semibold mb-3">Sun Path — {data.facade_solar.date}</h2>
            {sunPathChart(data.sun_path.samples)}
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="font-semibold mb-3">Facade Solar Exposure</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-3 py-2 font-semibold text-slate-700">Facade</th>
                    <th className="text-left px-3 py-2 font-semibold text-slate-700">Azimuth</th>
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">Daily POA (kWh/m²)</th>
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">Peak (W/m²)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {Object.entries(data.facade_solar.facades).map(([name, f]) => (
                    <tr key={name} className="hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium">{name}</td>
                      <td className="px-3 py-2 text-slate-600">{f.compass} ({f.azimuth_deg}°)</td>
                      <td className="px-3 py-2 text-right font-mono">{f.daily_poa_kwh_m2}</td>
                      <td className="px-3 py-2 text-right font-mono">{f.peak_poa_w_m2}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}