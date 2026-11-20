"use client";

import { useState } from "react";

export default function NewProjectPage() {
  const [step, setStep] = useState(1);

  return (
    <div className="max-w-2xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Create New Project</h1>
        <p className="text-slate-600 mt-2">Step {step} of 4 — Building information</p>
      </header>

      <div className="mb-8 flex gap-2">
        {[1, 2, 3, 4].map((s) => (
          <div
            key={s}
            className={`flex-1 h-2 rounded-full ${
              s <= step ? "bg-emerald-500" : "bg-slate-200"
            }`}
          />
        ))}
      </div>

      <form className="bg-white rounded-xl border border-slate-200 p-8 space-y-6">
        {step === 1 && (
          <>
            <h2 className="text-xl font-semibold mb-4">Project Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Project Name *</label>
                <input type="text" placeholder="e.g., Dhaka Residential Block A" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">City *</label>
                <input type="text" defaultValue="Dhaka" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Building Name (optional)</label>
              <input type="text" placeholder="Can be anonymized" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500" />
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="text-xl font-semibold mb-4">Building Configuration</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Building Type *</label>
                <select className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500">
                  <option>Residential</option>
                  <option>Mixed-use</option>
                  <option>Office</option>
                  <option>Commercial</option>
                  <option>Industrial</option>
                  <option>Institutional</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Number of Floors *</label>
                <input type="number" min="1" max="50" defaultValue="6" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Floor-to-Floor Height (m) *</label>
                <input type="number" step="0.1" min="2" max="6" defaultValue="3.0" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Total Floor Area (m²)</label>
                <input type="number" step="0.1" placeholder="Auto-calculated from rooms" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <h2 className="text-xl font-semibold mb-4">Site Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Plot Area (m²)</label>
                <input type="number" step="0.1" placeholder="For FAR calculation" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Building Footprint (m²)</label>
                <input type="number" step="0.1" placeholder="For coverage calculation" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Orientation (°)</label>
                <input type="number" min="0" max="360" defaultValue="0" placeholder="0 = North" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Construction Year</label>
                <input type="number" min="1900" max="2026" placeholder="e.g., 2020" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Structural System</label>
              <select className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500">
                <option value="">Select...</option>
                <option>Frame</option>
                <option>Shear-wall</option>
                <option>Moment-resisting</option>
                <option>Masonry</option>
                <option>Load-bearing brick</option>
                <option>Unknown</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Latitude</label>
                <input type="number" step="0.001" placeholder="23.8103" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Longitude</label>
                <input type="number" step="0.001" placeholder="90.4125" className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500" />
              </div>
            </div>
          </>
        )}

        {step === 4 && (
          <>
            <h2 className="text-xl font-semibold mb-4">Review &amp; Create</h2>
            <div className="bg-slate-50 rounded-lg p-4 space-y-2 text-sm">
              <p><span className="font-medium">Project:</span> Dhaka Residential Block A</p>
              <p><span className="font-medium">Building Type:</span> Residential</p>
              <p><span className="font-medium">Floors:</span> 6</p>
              <p><span className="font-medium">Floor Height:</span> 3.0 m</p>
              <p><span className="font-medium">City:</span> Dhaka</p>
            </div>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
              <p className="font-semibold">⚠️ Preliminary Analysis</p>
              <p className="mt-1">All calculations are screening-level estimates with documented assumptions.</p>
            </div>
          </>
        )}

        <div className="flex justify-between pt-6 border-t border-slate-200">
          <button
            type="button"
            onClick={() => setStep(Math.max(1, step - 1))}
            disabled={step === 1}
            className="px-6 py-2 border border-slate-300 rounded-lg font-medium hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            type="button"
            onClick={() => setStep(Math.min(4, step + 1))}
            disabled={step === 4}
            className="px-6 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {step === 4 ? "Create Project" : "Next"}
          </button>
        </div>
      </form>
    </div>
  );
}