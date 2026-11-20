/**
 * Pure, framework-free logic for the Create New Project wizard.
 *
 * Kept out of the React component so it can be unit-tested without a browser,
 * and so the exact same code validates input, builds the API payload, and
 * renders the review step. Nothing here may silently coerce or drop a value the
 * user typed.
 */

export interface ProjectForm {
  name: string;
  city: string;
  building_name: string;
  building_type: string;
  num_floors: string;
  floor_to_floor_height_m: string;
  total_floor_area: string;
  plot_area_m2: string;
  building_footprint_m2: string;
  orientation_deg: string;
  construction_year: string;
  structural_system: string;
  latitude: string;
  longitude: string;
}

export const BUILDING_TYPES = [
  "Residential",
  "Mixed-use",
  "Office",
  "Commercial",
  "Industrial",
  "Institutional",
  "Other",
] as const;

export const STRUCTURAL_SYSTEMS = [
  "Frame",
  "Shear-wall",
  "Moment-resisting",
  "Masonry",
  "Load-bearing brick",
  "Unknown",
] as const;

export const STEP_TITLES = [
  "Project Details",
  "Building Configuration",
  "Site Information",
  "Review & Create",
] as const;

export const INITIAL_FORM: ProjectForm = {
  name: "",
  city: "Dhaka",
  building_name: "",
  building_type: "Residential",
  num_floors: "6",
  floor_to_floor_height_m: "3.0",
  total_floor_area: "",
  plot_area_m2: "",
  building_footprint_m2: "",
  orientation_deg: "0",
  construction_year: "",
  structural_system: "",
  latitude: "",
  longitude: "",
};

/** Fields that must be non-empty before the wizard can advance. */
export const REQUIRED_BY_STEP: Record<number, (keyof ProjectForm)[]> = {
  1: ["name", "city"],
  2: ["num_floors", "floor_to_floor_height_m"],
  3: [],
  4: [],
};

export type FormErrors = Partial<Record<keyof ProjectForm, string>>;

function asNumber(value: string): number | null {
  const trimmed = value.trim();
  if (trimmed === "") return null;
  const n = Number(trimmed);
  return Number.isFinite(n) ? n : null;
}

/**
 * Validate the form up to and including `step`.
 * Returns an error map; an empty map means the step is valid.
 */
export function validateForm(
  form: ProjectForm,
  step: number
): FormErrors {
  const errors: FormErrors = {};

  if (step >= 1) {
    if (!form.name.trim()) {
      errors.name = "Project name is required.";
    }
    if (!form.city.trim()) {
      errors.city = "City is required.";
    }
  }

  if (step >= 2) {
    const floors = asNumber(form.num_floors);
    if (floors === null) {
      errors.num_floors = "Number of floors is required.";
    } else if (floors < 1 || floors > 50) {
      errors.num_floors = "Floors must be between 1 and 50.";
    } else if (!Number.isInteger(floors)) {
      errors.num_floors = "Floors must be a whole number.";
    }

    const height = asNumber(form.floor_to_floor_height_m);
    if (height === null) {
      errors.floor_to_floor_height_m = "Floor-to-floor height is required.";
    } else if (height < 2 || height > 6) {
      errors.floor_to_floor_height_m = "Height must be between 2 and 6 m.";
    }
  }

  if (step >= 3) {
    const plot = asNumber(form.plot_area_m2);
    if (form.plot_area_m2.trim() !== "" && (plot === null || plot <= 0)) {
      errors.plot_area_m2 = "Plot area must be a positive number.";
    }

    const footprint = asNumber(form.building_footprint_m2);
    if (form.building_footprint_m2.trim() !== "" && (footprint === null || footprint <= 0)) {
      errors.building_footprint_m2 = "Footprint must be a positive number.";
    } else if (
      footprint !== null &&
      plot !== null &&
      plot > 0 &&
      footprint > plot
    ) {
      // This mirrors the backend GeometryError so the user hears it here first.
      errors.building_footprint_m2 = "Footprint cannot exceed the plot area.";
    }

    const orientation = asNumber(form.orientation_deg);
    if (
      form.orientation_deg.trim() !== "" &&
      (orientation === null || orientation < 0 || orientation > 360)
    ) {
      errors.orientation_deg = "Orientation must be between 0 and 360 degrees.";
    }

    const year = asNumber(form.construction_year);
    if (form.construction_year.trim() !== "" && (year === null || year < 1900 || year > 2100)) {
      errors.construction_year = "Construction year must be between 1900 and 2100.";
    }

    const lat = asNumber(form.latitude);
    if (form.latitude.trim() !== "" && (lat === null || lat < -90 || lat > 90)) {
      errors.latitude = "Latitude must be between -90 and 90.";
    }

    const lon = asNumber(form.longitude);
    if (form.longitude.trim() !== "" && (lon === null || lon < -180 || lon > 180)) {
      errors.longitude = "Longitude must be between -180 and 180.";
    }
  }

  return errors;
}

/** The first step that currently has validation errors, or null if all valid. */
export function firstInvalidStep(form: ProjectForm): number | null {
  for (const step of [1, 2, 3]) {
    if (Object.keys(validateForm(form, step)).length > 0) return step;
  }
  return null;
}

/**
 * Build the POST /api/v1/projects body.
 *
 * Only includes optional fields the user actually filled in. Blank optional
 * fields are omitted rather than sent as null or 0, so the backend can apply
 * its own defaults instead of receiving a fabricated value.
 */
export function buildPayload(form: ProjectForm): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    name: form.name.trim(),
    city: form.city.trim(),
    building_type: form.building_type,
    num_floors: Number(form.num_floors),
    floor_to_floor_height_m: Number(form.floor_to_floor_height_m),
  };

  // Orientation defaults to 0 (North) when the user leaves it blank; this is a
  // documented default, not a silent guess.
  const orientation = asNumber(form.orientation_deg);
  payload.orientation_deg = orientation === null ? 0 : orientation;

  const optional: Array<[keyof ProjectForm, keyof ProjectForm]> = [
    ["building_name", "building_name"],
    ["plot_area_m2", "plot_area_m2"],
    ["building_footprint_m2", "building_footprint_m2"],
    ["construction_year", "construction_year"],
  ];

  for (const [field, key] of optional) {
    const raw = form[field].trim();
    if (raw !== "") {
      const n = asNumber(raw);
      payload[key] = n === null ? raw : n;
    }
  }

  if (form.structural_system.trim() !== "") {
    payload.structural_system = form.structural_system.trim();
  }

  const lat = asNumber(form.latitude);
  if (lat !== null) payload.latitude = lat;

  const lon = asNumber(form.longitude);
  if (lon !== null) payload.longitude = lon;

  return payload;
}

export interface ReviewRow {
  label: string;
  value: string;
}

/** Rows shown on the review step, derived from what the user actually entered. */
export function reviewRows(form: ProjectForm): ReviewRow[] {
  const display = (v: string, fallback: string) =>
    v.trim() === "" ? fallback : v.trim();

  const height = form.floor_to_floor_height_m.trim();
  const orientation = asNumber(form.orientation_deg);

  return [
    { label: "Project", value: display(form.name, "—") },
    { label: "City", value: display(form.city, "—") },
    { label: "Building Name", value: display(form.building_name, "Not provided") },
    { label: "Building Type", value: form.building_type },
    { label: "Floors", value: display(form.num_floors, "—") },
    { label: "Floor Height", value: height === "" ? "—" : `${height} m` },
    {
      label: "Orientation",
      value:
        form.orientation_deg.trim() === ""
          ? "0° (default North)"
          : orientation === null
            ? form.orientation_deg
            : `${orientation}°`,
    },
    {
      label: "Plot Area",
      value: form.plot_area_m2.trim() === "" ? "Not provided" : `${form.plot_area_m2.trim()} m²`,
    },
    {
      label: "Footprint",
      value:
        form.building_footprint_m2.trim() === "" ? "Not provided" : `${form.building_footprint_m2.trim()} m²`,
    },
    { label: "Construction Year", value: display(form.construction_year, "Not provided") },
    { label: "Structural System", value: display(form.structural_system, "Not provided (will be flagged)") },
    {
      label: "Coordinates",
      value:
        form.latitude.trim() === "" && form.longitude.trim() === ""
          ? "Not provided"
          : `${display(form.latitude, "—")}, ${display(form.longitude, "—")}`,
    },
    {
      label: "Total Floor Area",
      value:
        form.total_floor_area.trim() === ""
          ? "Derived from rooms"
          : `${form.total_floor_area.trim()} m²`,
    },
  ];
}