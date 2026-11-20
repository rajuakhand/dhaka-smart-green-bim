"use client";

import { useState } from "react";

export default function BuildingSetupPage() {
  const [tab, setTab] = useState("info");

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-slate-900">Building Setup</h1>
        <p className="text-slate-600 mt-2">Module A — Building metadata, geometry, orientation, materials</p>
      </header>

      <div className="flex gap-2 border-b border-slate-200 pb-2">
        {[
          { id: "info", label: "Building Info" },
          { id: "geometry", label: "Geometry" },
          { id: "materials", label: "Materials" },
          { id: "site", label: "Site Context" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              tab === t.id
                ? "bg-emerald-600 text-white"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        {tab === "info" && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Building Information</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Project Name *</label>
                <input type="text" value="Dhaka Residential Block A" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">City *</label>
                <input type="text" value="Dhaka" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Building Type *</label>
                <select value="Residential" disabled className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg">
                  <option>Residential</option>
                  <option>Mixed-use</option>
                  <option>Office</option>
                  <option>Commercial</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Number of Floors *</label>
                <input type="number" value="6" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Floor-to-Floor Height (m) *</label>
                <input type="number" value="3.0" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Construction Year</label>
                <input type="number" value="2020" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
              </div>
            </div>
          </div>
        )}

        {tab === "geometry" && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Building Geometry</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Total Floor Area (m²)</label>
                <input type="number" value="1200" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
                <p className="text-xs text-slate-500 mt-1">Auto-calculated from room inputs</p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Building Footprint (m²)</label>
                <input type="number" value="200" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Plot Area (m²)</label>
                <input type="number" value="500" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Orientation (°)</label>
                <input type="number" value="0" readOnly className="w-full px-4 py-3 border border-slate-200 bg-slate-50 rounded-lg" />
                <p className="text-xs text-slate-500 mt-1">0° = North, 90° = East, 180° = South, 270° = West</p>
              </div>
            </div>
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-sm">
              <p className="font-semibold text-emerald-900">Geometry Validation: ✅ Passed</p>
              <p className="text-emerald-800 mt-1">Building footprint fits within plot area. No geometry errors detected.</p>
            </div>
          </div>
        )}

        {tab === "materials" && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Material Properties</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Wall Material</label>
                <select className="w-full px-4 py-3 border border-slate-300 rounded-lg">
                  <option>Brick (150mm) + Plaster</option>
                  <option>Concrete Block</option>
                  <option>Brick + Insulation</option>
                  <option>Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Roof Material</label>
                <select className="w-full px-4 py-3 border border-slate-300 rounded-lg">
                  <option>Concrete Slab</option>
                  <option>Tin/Corrugated Iron</option>
                  <option>Concrete + Insulation</option>
                  <option>Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Glazing Type</label>
                <select className="w-full px-4 py-3 border border-slate-300 rounded-lg">
                  <option>Clear</option>
                  <option>Tinted</option>
                  <option>Double low-E</option>
                  <option>Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">External Wall U-Value (W/m²K)</label>
                <input type="number" step="0.1" value="2.0" className="w-full px-4 py-3 border border-slate-300 rounded-lg" />
              </div>
            </div>
            <p className="text-xs text-slate-500 mt-4">
              Material properties affect energy calculations. Values should be verified from manufacturer data or BNBC.
            </p>
          </div>
        )}

        {tab === "site" && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold">Site Context</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">Surrounding Building Height (m)</label>
                <input type="number" placeholder="Max height of adjacent buildings" className="w-full px-4 py-3 border border-slate-300 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Distance to Nearest Building (m)</label>
                <input type="number" placeholder="Horizontal distance" className="w-full px-4 py-3 border border-slate-300 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">RAJUK DAP Zone</label>
                <input type="text" placeholder="e.g., Mirpur, Dhanmondi" className="w-full px-4 py-3 border border-slate-300 rounded-lg" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">GPS Coordinates</label>
                <div className="flex gap-2">
                  <input type="number" step="0.001" placeholder="23.8103" className="flex-1 px-4 py-3 border border-slate-300 rounded-lg" />
                  <input type="number" step="0.001" placeholder="90.4125" className="flex-1 px-4 py-3 border border-slate-300 rounded-lg" />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-end">
        <button className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700">
          Save &amp; Continue to Rooms
        </button>
      </div>
    </div>
  );
}