"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Layer = { name: string; thickness_mm: number; conductivity_w_mk: number; source_id: string };
type Assembly = {
  assembly_id: string;
  name: string;
  category: string;
  layers: Layer[];
  u_value_w_m2k: number;
  source_id: string;
  verification: string;
  notes: string;
};
type Glazing = {
  assembly_id: string;
  name: string;
  u_value_w_m2k: number;
  shgc: number;
  vt: number;
  verification: string;
};
type Data = {
  opaque: { unit: string; method: string; assemblies: Assembly[] };
  glazing: { unit: string; assemblies: Glazing[] };
  surface_resistances: { Rsi_m2k_w: number; Rse_m2k_w: number };
  limitations: string[];
};

export default function MaterialsPage() {
  const [data, setData] = useState<Data | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API}/api/v1/phase2/materials`)
      .then((r) => r.json())
      .then(setData)
      .catch((e) => setErr(String(e)));
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Material Database</h1>
        <p className="text-slate-600 mt-2">
          Local construction assemblies with ISO 6946 derived U-values
        </p>
      </header>

      {err && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{err}</div>
      )}

      {!data && !err && (
        <div className="bg-slate-50 rounded-xl p-8 text-center text-sm text-slate-500">Loading…</div>
      )}

      {data && (
        <>
          <div className="grid md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 bg-white rounded-xl border border-slate-200">
              <div className="text-slate-500">Opaque method</div>
              <div className="font-medium mt-1">{data.opaque.method}</div>
            </div>
            <div className="p-4 bg-white rounded-xl border border-slate-200">
              <div className="text-slate-500">Surface resistances</div>
              <div className="font-medium mt-1 font-mono">
                Rsi = {data.surface_resistances.Rsi_m2k_w} · Rse = {data.surface_resistances.Rse_m2k_w} m²K/W
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="font-semibold mb-3">Opaque Assemblies</h2>
            <div className="space-y-3">
              {data.opaque.assemblies.map((a) => (
                <div key={a.assembly_id} className="p-4 border border-slate-200 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium text-sm">{a.name}</div>
                      <div className="text-[11px] text-slate-500 font-mono mt-0.5">{a.assembly_id}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold text-slate-900">{a.u_value_w_m2k}</div>
                      <div className="text-[10px] text-slate-500">W/m²K</div>
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {a.layers.map((l, i) => (
                      <span key={i} className="px-1.5 py-0.5 bg-slate-100 rounded text-[10px]">
                        {l.name} {l.thickness_mm}mm · k={l.conductivity_w_mk}
                      </span>
                    ))}
                  </div>
                  <div className="mt-2 text-[10px] text-amber-700">
                    ⚠ {a.verification}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h2 className="font-semibold mb-3">Glazing</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-3 py-2 font-semibold text-slate-700">Type</th>
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">U (W/m²K)</th>
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">SHGC</th>
                    <th className="text-right px-3 py-2 font-semibold text-slate-700">VT</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.glazing.assemblies.map((g) => (
                    <tr key={g.assembly_id} className="hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium">{g.name}</td>
                      <td className="px-3 py-2 text-right font-mono">{g.u_value_w_m2k}</td>
                      <td className="px-3 py-2 text-right font-mono">{g.shgc}</td>
                      <td className="px-3 py-2 text-right font-mono">{g.vt}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
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