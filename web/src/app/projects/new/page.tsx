"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import {
  BUILDING_TYPES,
  INITIAL_FORM,
  STEP_TITLES,
  STRUCTURAL_SYSTEMS,
  buildPayload,
  firstInvalidStep,
  reviewRows,
  validateForm,
  type FormErrors,
  type ProjectForm,
} from "../../../../lib/project-form";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const REQUIRED_FIELDS: Array<keyof ProjectForm> = [
  "name",
  "city",
  "num_floors",
  "floor_to_floor_height_m",
];

export default function NewProjectPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<ProjectForm>(INITIAL_FORM);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  function update<K extends keyof ProjectForm>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
    setErrors((prev) => {
      if (!prev[key]) return prev;
      const next = { ...prev };
      delete next[key];
      return next;
    });
    setServerError(null);
  }

  function goNext() {
    const found = validateForm(form, step);
    setErrors(found);
    if (Object.keys(found).length === 0) {
      setStep((s) => Math.min(4, s + 1));
    }
  }

  function goBack() {
    setErrors({});
    setStep((s) => Math.max(1, s - 1));
  }

  function jumpTo(target: number) {
    if (target < step) {
      setErrors({});
      setStep(target);
    } else if (target === step + 1) {
      goNext();
    }
  }

  async function submit() {
    const badStep = firstInvalidStep(form);
    if (badStep !== null) {
      setStep(badStep);
      setErrors(validateForm(form, badStep));
      return;
    }

    setSubmitting(true);
    setServerError(null);
    try {
      const res = await fetch(`${API}/api/v1/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload(form)),
      });

      const body = await res.json().catch(() => null);

      if (!res.ok) {
        const detail = body?.detail;
        const message = Array.isArray(detail)
          ? detail.map((d: any) => d?.msg ?? JSON.stringify(d)).join("; ")
          : typeof detail === "string"
            ? detail
            : `Request failed (HTTP ${res.status})`;
        throw new Error(message);
      }

      if (!body?.id) {
        throw new Error("The server did not return a project id.");
      }

      router.push(`/projects/${body.id}`);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Could not create the project.");
      setSubmitting(false);
    }
  }

  function field(
    label: string,
    key: keyof ProjectForm,
    opts: {
      type?: string;
      step?: string;
      min?: string | number;
      max?: string | number;
      placeholder?: string;
    } = {}
  ) {
    const id = `field-${key}`;
    return (
      <div>
        <label htmlFor={id} className="block text-sm font-medium mb-2">
          {label}
          {REQUIRED_FIELDS.includes(key) && <span className="text-red-500"> *</span>}
        </label>
        <input
          id={id}
          name={key}
          type={opts.type ?? "text"}
          step={opts.step}
          min={opts.min}
          max={opts.max}
          value={form[key]}
          placeholder={opts.placeholder}
          onChange={(e) => update(key, e.target.value)}
          aria-invalid={errors[key] ? true : undefined}
          aria-describedby={errors[key] ? `${id}-error` : undefined}
          className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 ${
            errors[key] ? "border-red-400" : "border-slate-300"
          }`}
        />
        {errors[key] && (
          <p id={`${id}-error`} className="mt-1 text-xs text-red-600">
            {errors[key]}
          </p>
        )}
      </div>
    );
  }

  const review = reviewRows(form);

  return (
    <div className="max-w-2xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Create New Project</h1>
        <p className="text-slate-600 mt-2">
          Step {step} of 4 — {STEP_TITLES[step - 1]}
        </p>
      </header>

      <div className="mb-8 flex gap-2">
        {[1, 2, 3, 4].map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => jumpTo(s)}
            aria-label={`Go to step ${s}`}
            aria-current={s === step ? "step" : undefined}
            className={`flex-1 h-2 rounded-full transition-colors ${
              s <= step ? "bg-emerald-500" : "bg-slate-200"
            }`}
          />
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (step < 4) goNext();
          else void submit();
        }}
        className="bg-white rounded-xl border border-slate-200 p-8 space-y-6"
        noValidate
      >
        {step === 1 && (
          <>
            <h2 className="text-xl font-semibold mb-4">Project Details</h2>
            <div className="grid grid-cols-2 gap-4">
              {field("Project Name", "name", { placeholder: "e.g., Dhaka Residential Block A" })}
              {field("City", "city", { placeholder: "Dhaka" })}
            </div>
            {field("Building Name (optional)", "building_name", {
              placeholder: "Can be anonymized",
            })}
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="text-xl font-semibold mb-4">Building Configuration</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="field-building_type" className="block text-sm font-medium mb-2">
                  Building Type <span className="text-red-500">*</span>
                </label>
                <select
                  id="field-building_type"
                  name="building_type"
                  value={form.building_type}
                  onChange={(e) => update("building_type", e.target.value)}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
                >
                  {BUILDING_TYPES.map((t) => (
                    <option key={t}>{t}</option>
                  ))}
                </select>
              </div>
              {field("Number of Floors", "num_floors", { type: "number", min: 1, max: 50 })}
              {field("Floor-to-Floor Height (m)", "floor_to_floor_height_m", {
                type: "number",
                step: "0.1",
                min: 2,
                max: 6,
              })}
              {field("Total Floor Area (m²)", "total_floor_area", {
                type: "number",
                step: "0.1",
                placeholder: "Optional — usually derived from rooms",
              })}
            </div>
            <p className="text-xs text-slate-500">
              Total floor area is calculated from the rooms you add after creating the project.
            </p>
          </>
        )}

        {step === 3 && (
          <>
            <h2 className="text-xl font-semibold mb-4">Site Information</h2>
            <div className="grid grid-cols-2 gap-4">
              {field("Plot Area (m²)", "plot_area_m2", {
                type: "number",
                step: "0.1",
                placeholder: "For FAR calculation",
              })}
              {field("Building Footprint (m²)", "building_footprint_m2", {
                type: "number",
                step: "0.1",
                placeholder: "For coverage calculation",
              })}
              {field("Orientation (°)", "orientation_deg", {
                type: "number",
                min: 0,
                max: 360,
                placeholder: "0 = North",
              })}
              {field("Construction Year", "construction_year", {
                type: "number",
                min: 1900,
                max: 2100,
                placeholder: "e.g., 2020",
              })}
            </div>
            <div>
              <label htmlFor="field-structural_system" className="block text-sm font-medium mb-2">
                Structural System
              </label>
              <select
                id="field-structural_system"
                name="structural_system"
                value={form.structural_system}
                onChange={(e) => update("structural_system", e.target.value)}
                className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
              >
                <option value="">Select… (unknown is acceptable)</option>
                {STRUCTURAL_SYSTEMS.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
              <p className="mt-1 text-xs text-slate-500">
                Leaving this blank is fine — structural screening will flag it as missing information.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {field("Latitude", "latitude", {
                type: "number",
                step: "0.0001",
                placeholder: "23.8103 (Dhaka)",
              })}
              {field("Longitude", "longitude", {
                type: "number",
                step: "0.0001",
                placeholder: "90.4125 (Dhaka)",
              })}
            </div>
          </>
        )}

        {step === 4 && (
          <>
            <h2 className="text-xl font-semibold mb-4">Review &amp; Create</h2>
            <div className="bg-slate-50 rounded-lg p-4 space-y-2 text-sm">
              {review.map((row) => (
                <div key={row.label} className="flex justify-between gap-4">
                  <span className="text-slate-500 shrink-0">{row.label}</span>
                  <span className="font-medium text-right break-words">{row.value}</span>
                </div>
              ))}
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
              <p className="font-semibold">⚠️ Preliminary Analysis</p>
              <p className="mt-1">
                All calculations are screening-level estimates with documented assumptions.
                Nothing here is a compliance certificate or a substitute for professional review.
              </p>
            </div>

            {serverError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
                <p className="font-semibold">Could not create the project</p>
                <p className="mt-1 break-words">{serverError}</p>
              </div>
            )}
          </>
        )}

        <div className="flex justify-between pt-6 border-t border-slate-200">
          <button
            type="button"
            onClick={goBack}
            disabled={step === 1 || submitting}
            className="px-6 py-2 border border-slate-300 rounded-lg font-medium hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? "Creating…" : step === 4 ? "Create Project" : "Next"}
          </button>
        </div>
      </form>
    </div>
  );
}