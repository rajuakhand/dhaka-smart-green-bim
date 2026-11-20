"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type ModuleCard = {
  key: string;
  title: string;
  method: string;
  status: string;
  confidence: string;
  href: string;
  icon: string;
};

const MODULES: ModuleCard[] = [
  {
    key: "climate",
    title: "Climate Data",
    method: "NASA POWER monthly normals",
    status: "Calculated",
    confidence: "High",
    href: "/phase2/climate",
    icon: "🌦️",
  },
  {
    key: "solar",
    title: "Solar Geometry",
    method: "NREL SPA + Ineichen-Perez",
    status: "Calculated",
    confidence: "Medium",
    href: "/phase2/solar",
    icon: "☀️",
  },
  {
    key: "daylight",
    title: "Daylight Factor",
    method: "CIBSE/SLL LG10 (BRE)",
    status: "Calculated",
    confidence: "Medium",
    href: "/phase2/daylight",
    icon: "💡",
  },
  {
    key: "shading",
    title: "Shading Analysis",
    method: "Geometric profile angles",
    status: "Calculated",
    confidence: "Medium",
    href: "/phase2/shading",
    icon: "🌥️",
  },
  {
    key: "sensitivity",
    title: "Sensitivity Analysis",
    method: "One-at-a-time perturbation",
    status: "Calculated",
    confidence: "Medium",
    href: "/phase2/sensitivity",
    icon: "📈",
  },
  {
    key: "optimization",
    title: "Parametric Optimization",
    method: "Exhaustive grid search",
    status: "Calculated",
    confidence: "Medium",
    href: "/phase2/optimization",
    icon: "🎯",
  },
  {
    key: "materials",
    title: "Material Database",
    method: "ISO 6946 derived U-values",
    status: "Calculated",
    confidence: "Medium",
    href: "/phase2/materials",
    icon: "🧱",
  },
];

type Capability = {
  engines: { energyplus: { available: boolean; install_hint: string }; radiance: { available: boolean; install_hint: string } };
  any_engine_available: boolean;
  principle: string;
};

export default function Phase2Page() {
  const [capability, setCapability] = useState<Capability | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/phase2/simulation-capability`)
      .then((r) => r.json())
      .then(setCapability)
      .catch(() => setCapability(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <header>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold text-slate-900">Phase 2 — Advanced Analysis</h1>
          <span className="px-3 py-1 bg-violet-100 text-violet-700 text-xs font-semibold rounded-full">
            Physics-Based
          </span>
        </div>
        <p className="text-slate-600 mt-2">
          Deterministic engineering calculations using verified astronomical models and
          published methods. No external simulation engine required.
        </p>
      </header>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {MODULES.map((m) => (
          <a
            key={m.key}
            href={m.href}
            className="p-5 bg-white rounded-xl border border-slate-200 hover:border-violet-400 hover:shadow-sm transition-all block"
          >
            <div className="text-2xl mb-2">{m.icon}</div>
            <h3 className="font-semibold text-slate-900">{m.title}</h3>
            <p className="text-xs text-slate-500 mt-1">{m.method}</p>
            <div className="mt-3 flex gap-2 flex-wrap">
              <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 text-[10px] font-medium rounded">
                {m.status}
              </span>
              <span className="px-2 py-0.5 bg-slate-100 text-slate-600 text-[10px] rounded">
                {m.confidence}
              </span>
            </div>
          </a>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        <h2 className="text-xl font-semibold mb-4">Simulation Engine Status</h2>
        <p className="text-sm text-slate-600 mb-4">
          Full hourly energy simulation and climate-based daylight (sDA/ASE) require
          external engines. The platform reports their availability honestly and never
          presents a value as simulated when no simulation ran.
        </p>

        {loading ? (
          <p className="text-sm text-slate-400">Checking engines…</p>
        ) : capability ? (
          <div className="grid md:grid-cols-2 gap-4">
            {[
              {
                name: "EnergyPlus",
                info: capability.engines.energyplus,
                use: "Hourly energy simulation",
              },
              {
                name: "Radiance",
                info: capability.engines.radiance,
                use: "Climate-based daylight (sDA/ASE)",
              },
            ].map((engine) => (
              <div
                key={engine.name}
                className={`p-4 rounded-lg border ${
                  engine.info.available
                    ? "bg-emerald-50 border-emerald-200"
                    : "bg-amber-50 border-amber-200"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-sm">{engine.name}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${
                      engine.info.available
                        ? "bg-emerald-200 text-emerald-800"
                        : "bg-amber-200 text-amber-800"
                    }`}
                  >
                    {engine.info.available ? "Available" : "Not installed"}
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-1">{engine.use}</p>
                {!engine.info.available && (
                  <p className="text-[11px] text-slate-500 mt-2 leading-relaxed">
                    {engine.info.install_hint}
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-red-600">Could not reach the backend API.</p>
        )}

        <div className="mt-4 p-3 bg-slate-50 rounded-lg text-xs text-slate-600">
          <strong>Principle:</strong> {capability?.principle || "Never report simulated values when no simulation was run."}
        </div>
      </div>

      <div className="bg-violet-50 border border-violet-200 rounded-xl p-6">
        <h3 className="font-semibold text-violet-900">What is calculated vs simulated</h3>
        <div className="grid md:grid-cols-2 gap-4 mt-3 text-sm">
          <div>
            <p className="font-medium text-emerald-700 mb-1">Calculated (this phase)</p>
            <ul className="list-disc list-inside text-slate-700 space-y-0.5 text-xs">
              <li>Solar position &amp; clear-sky irradiance</li>
              <li>Surface solar heat gain</li>
              <li>Daylight factor (CIBSE/BRE)</li>
              <li>Geometric shading</li>
              <li>Envelope U-values (ISO 6946)</li>
              <li>Sensitivity &amp; parametric search</li>
            </ul>
          </div>
          <div>
            <p className="font-medium text-amber-700 mb-1">Not evaluated (needs engine)</p>
            <ul className="list-disc list-inside text-slate-700 space-y-0.5 text-xs">
              <li>Hourly building energy simulation</li>
              <li>sDA / ASE climate-based daylight</li>
              <li>Full 3D obstruction shading</li>
              <li>Annual shade fraction</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}