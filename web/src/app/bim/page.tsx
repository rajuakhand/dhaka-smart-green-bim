"use client";

import { useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Capability = {
  engines: {
    ifcopenshell: { available: boolean; version: string | null; error: string | null; install_hint: string };
  };
  any_engine_available: boolean;
  capabilities: Record<string, boolean>;
  supported_schemas: string[];
  max_upload_size_mb: number;
  principle: string;
};

type ModelSummary = {
  file: { name: string; size_bytes: number; schema: string };
  units: { length_unit: string; length_scale_to_metres: number; note: string };
  hierarchy: { project: string | null; building: string | null; storeys: string[] };
  counts: Record<string, number>;
  areas: {
    total_space_floor_area_m2: number;
    total_envelope_area_m2: number;
    total_window_area_m2: number;
  };
  warnings: string[];
  unsupported_geometry_count: number;
  limitations: string[];
  status: string;
  confidence: string;
};

type AnalysisRoom = {
  name: string;
  room_type: string;
  room_type_inferred: boolean;
  length_m: number;
  width_m: number;
  height_m: number;
  floor_area_m2: number;
  volume_m3: number;
  window_area_m2: number | null;
  storey: string | null;
};

type AnalysisModel = {
  rooms: AnalysisRoom[];
  room_count: number;
  total_floor_area_m2: number;
  total_volume_m3: number;
  envelope: {
    wall_area_m2: number;
    slab_area_m2: number;
    roof_area_m2: number;
    glazing_area_m2: number;
    envelope_area_m2: number;
    glazing_ratio_percent: number | null;
    wall_count: number;
    window_count: number;
    door_count: number;
  };
  footprint_m2: number | null;
  openings: { method: string; is_authoritative: boolean; disclosure: string; unassigned_windows: string[] };
  warnings: string[];
  limitations: string[];
  status: string;
  confidence: string;
};

type ValidationReport = {
  valid: boolean;
  summary: { errors: number; warnings: number; notes: number };
  errors: { code: string; message: string }[];
  warnings: { code: string; message: string }[];
  notes: { code: string; message: string }[];
};

type AnalyzeResponse = {
  executed: boolean;
  file?: string;
  model?: ModelSummary;
  validation?: ValidationReport;
  analysis_model?: AnalysisModel;
  detail?: string;
};

export default function BimPage() {
  const [capability, setCapability] = useState<Capability | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  async function loadCapability() {
    try {
      const r = await fetch(`${API}/api/v1/bim/capability`);
      setCapability(await r.json());
    } catch {
      setCapability(null);
    }
  }

  if (!capability && typeof window !== "undefined") {
    loadCapability();
  }

  async function upload(file: File) {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await fetch(`${API}/api/v1/bim/upload`, { method: "POST", body: fd });
      const j = await r.json();
      if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
      setResult(j);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-bold text-slate-900">BIM Integration</h1>
          <span className="px-3 py-1 bg-sky-100 text-sky-700 text-xs font-semibold rounded-full">
            Phase 3
          </span>
        </div>
        <p className="text-slate-600 mt-2">
          IFC upload, geometry extraction, validation and conversion to the analysis model
        </p>
      </header>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="font-semibold mb-3">IfcOpenShell Engine</h2>
        {capability ? (
          <>
            <div className="flex items-center gap-3">
              <span
                className={`w-3 h-3 rounded-full ${
                  capability.any_engine_available ? "bg-emerald-500" : "bg-amber-500"
                }`}
              />
              <span className="text-sm font-medium">
                {capability.any_engine_available ? "Available" : "Not available"}
                {capability.engines.ifcopenshell.version && (
                  <span className="text-slate-500 font-normal">
                    {" "}· version {capability.engines.ifcopenshell.version}
                  </span>
                )}
              </span>
            </div>
            {!capability.any_engine_available && (
              <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800">
                {capability.engines.ifcopenshell.install_hint}
              </div>
            )}
            <div className="mt-4 flex flex-wrap gap-2">
              {Object.entries(capability.capabilities).map(([k, v]) => (
                <span
                  key={k}
                  className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                    v ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-500"
                  }`}
                >
                  {v ? "✓" : "✕"} {k.replace(/_/g, " ")}
                </span>
              ))}
            </div>
            <div className="mt-3 text-[11px] text-slate-500">
              Schemas: {capability.supported_schemas.join(", ")} · Max upload{" "}
              {capability.max_upload_size_mb} MB
            </div>
          </>
        ) : (
          <p className="text-sm text-slate-400">Checking engine…</p>
        )}
      </div>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          const f = e.dataTransfer.files?.[0];
          if (f) upload(f);
        }}
        className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors ${
          dragOver ? "border-sky-400 bg-sky-50" : "border-slate-300 bg-white"
        }`}
      >
        <div className="text-4xl mb-3">📐</div>
        <p className="text-sm text-slate-600 mb-1">Drop an .ifc file here</p>
        <p className="text-xs text-slate-400 mb-4">or choose a file · limit {capability?.max_upload_size_mb ?? 25} MB</p>
        <input
          ref={fileRef}
          type="file"
          accept=".ifc"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) upload(f);
          }}
        />
        <button
          onClick={() => fileRef.current?.click()}
          disabled={busy}
          className="px-5 py-2 bg-sky-600 text-white rounded-lg text-sm font-medium hover:bg-sky-700 disabled:opacity-50"
        >
          {busy ? "Uploading…" : "Choose IFC file"}
        </button>
        <div className="mt-4">
          <button
            onClick={async () => {
              setBusy(true); setError(null);
              try {
                const r = await fetch(`${API}/api/v1/bim/analyze`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ file_path: "tests/fixtures/sample_m.ifc", validate: true }),
                });
                const j = await r.json();
                if (!r.ok) throw new Error(j.detail || `HTTP ${r.status}`);
                setResult(j);
              } catch (e) {
                setError(e instanceof Error ? e.message : "Analysis failed");
              } finally { setBusy(false); }
            }}
            className="text-xs text-slate-500 underline hover:text-slate-700"
          >
            Try the bundled sample model
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {result?.executed === false && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
          <h3 className="font-semibold text-amber-900">Not evaluated</h3>
          <p className="text-sm text-amber-800 mt-1">{result.detail}</p>
        </div>
      )}

      {result?.model && (
        <>
          <div className="grid md:grid-cols-4 gap-4">
            {[
              { label: "Schema", value: result.model.file.schema },
              { label: "Length Unit", value: result.model.units.length_unit },
              { label: "Floor Area", value: `${result.model.areas.total_space_floor_area_m2} m²` },
              { label: "Envelope", value: `${result.model.areas.total_envelope_area_m2} m²` },
            ].map((s) => (
              <div key={s.label} className="p-4 bg-white rounded-xl border border-slate-200">
                <div className="text-xs text-slate-500">{s.label}</div>
                <div className="text-xl font-bold text-slate-900 mt-1">{s.value}</div>
              </div>
            ))}
          </div>

          {result.validation && (
            <div
              className={`rounded-xl border p-5 ${
                result.validation.valid
                  ? "bg-emerald-50 border-emerald-200"
                  : "bg-red-50 border-red-200"
              }`}
            >
              <h3 className="font-semibold">
                {result.validation.valid ? "✓ Validation passed" : "⚠ Validation issues"}
              </h3>
              <p className="text-xs mt-1 opacity-80">
                {result.validation.summary.errors} errors ·{" "}
                {result.validation.summary.warnings} warnings ·{" "}
                {result.validation.summary.notes} notes
              </p>
              {[...result.validation.errors, ...result.validation.warnings].slice(0, 5).map((i, idx) => (
                <p key={idx} className="text-xs mt-2">
                  <span className="font-mono opacity-70">[{i.code}]</span> {i.message}
                </p>
              ))}
            </div>
          )}

          {result.analysis_model && (
            <>
              <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="font-semibold mb-3">
                  Extracted Rooms ({result.analysis_model.room_count})
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50">
                      <tr>
                        <th className="text-left px-3 py-2 font-semibold text-slate-700">Room</th>
                        <th className="text-left px-3 py-2 font-semibold text-slate-700">Type</th>
                        <th className="text-right px-3 py-2 font-semibold text-slate-700">L × W × H (m)</th>
                        <th className="text-right px-3 py-2 font-semibold text-slate-700">Area (m²)</th>
                        <th className="text-right px-3 py-2 font-semibold text-slate-700">Volume (m³)</th>
                        <th className="text-right px-3 py-2 font-semibold text-slate-700">Window (m²)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {result.analysis_model.rooms.map((room, i) => (
                        <tr key={i} className="hover:bg-slate-50">
                          <td className="px-3 py-2 font-medium">{room.name}</td>
                          <td className="px-3 py-2">
                            <span className={`px-2 py-0.5 rounded text-[10px] ${
                              room.room_type_inferred ? "bg-sky-50 text-sky-700" : "bg-amber-50 text-amber-700"
                            }`}>
                              {room.room_type}
                            </span>
                          </td>
                          <td className="px-3 py-2 text-right font-mono text-xs">
                            {room.length_m} × {room.width_m} × {room.height_m}
                          </td>
                          <td className="px-3 py-2 text-right font-mono">{room.floor_area_m2}</td>
                          <td className="px-3 py-2 text-right font-mono">{room.volume_m3}</td>
                          <td className="px-3 py-2 text-right font-mono">
                            {room.window_area_m2 ?? "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white rounded-xl border border-slate-200 p-6">
                  <h3 className="font-semibold text-sm mb-2">Envelope</h3>
                  <div className="space-y-1 text-xs">
                    {[
                      ["Walls", `${result.analysis_model.envelope.wall_area_m2} m²`],
                      ["Slabs", `${result.analysis_model.envelope.slab_area_m2} m²`],
                      ["Glazing", `${result.analysis_model.envelope.glazing_area_m2} m²`],
                      ["Glazing ratio", `${result.analysis_model.envelope.glazing_ratio_percent ?? "—"} %`],
                      ["Footprint", `${result.analysis_model.footprint_m2 ?? "—"} m²`],
                    ].map(([k, v]) => (
                      <div key={k} className="flex justify-between">
                        <span className="text-slate-500">{k}</span>
                        <span className="font-mono">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                  <h3 className="font-semibold text-xs text-amber-900 mb-2">Openings disclosure</h3>
                  <p className="text-[11px] text-amber-800 leading-relaxed">
                    {result.analysis_model.openings.disclosure}
                  </p>
                </div>
              </div>

              {result.analysis_model.warnings.length > 0 && (
                <div className="bg-white rounded-xl border border-slate-200 p-6">
                  <h3 className="font-semibold text-sm mb-2">Conversion warnings</h3>
                  <ul className="list-disc list-inside text-xs text-slate-600 space-y-1">
                    {result.analysis_model.warnings.map((w, i) => <li key={i}>{w}</li>)}
                  </ul>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}