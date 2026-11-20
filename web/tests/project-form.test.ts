import { describe, expect, it } from "vitest";

import {
  INITIAL_FORM,
  buildPayload,
  firstInvalidStep,
  reviewRows,
  validateForm,
  type ProjectForm,
} from "../lib/project-form";

/** Build a fully valid form, then apply overrides per test. */
function validForm(overrides: Partial<ProjectForm> = {}): ProjectForm {
  return {
    ...INITIAL_FORM,
    name: "Dhaka Residential Block A",
    city: "Dhaka",
    building_type: "Residential",
    num_floors: "6",
    floor_to_floor_height_m: "3.0",
    ...overrides,
  };
}

describe("validateForm", () => {
  it("accepts a minimal valid form", () => {
    expect(validateForm(validForm(), 3)).toEqual({});
  });

  it("requires a project name", () => {
    const errors = validateForm(validForm({ name: "   " }), 1);
    expect(errors.name).toBeTruthy();
  });

  it("requires a city", () => {
    const errors = validateForm(validForm({ city: "" }), 1);
    expect(errors.city).toBeTruthy();
  });

  it("rejects zero floors", () => {
    const errors = validateForm(validForm({ num_floors: "0" }), 2);
    expect(errors.num_floors).toBeTruthy();
  });

  it("rejects more than 50 floors", () => {
    const errors = validateForm(validForm({ num_floors: "51" }), 2);
    expect(errors.num_floors).toBeTruthy();
  });

  it("rejects a non-integer floor count", () => {
    const errors = validateForm(validForm({ num_floors: "6.5" }), 2);
    expect(errors.num_floors).toBeTruthy();
  });

  it("rejects a floor height below 2 m", () => {
    const errors = validateForm(validForm({ floor_to_floor_height_m: "1.5" }), 2);
    expect(errors.floor_to_floor_height_m).toBeTruthy();
  });

  it("rejects a floor height above 6 m", () => {
    const errors = validateForm(validForm({ floor_to_floor_height_m: "7" }), 2);
    expect(errors.floor_to_floor_height_m).toBeTruthy();
  });

  it("rejects a footprint larger than the plot", () => {
    const errors = validateForm(
      validForm({ plot_area_m2: "500", building_footprint_m2: "600" }),
      3
    );
    expect(errors.building_footprint_m2).toMatch(/cannot exceed/i);
  });

  it("accepts a footprint equal to the plot", () => {
    const errors = validateForm(
      validForm({ plot_area_m2: "500", building_footprint_m2: "500" }),
      3
    );
    expect(errors.building_footprint_m2).toBeUndefined();
  });

  it("rejects a negative plot area", () => {
    const errors = validateForm(validForm({ plot_area_m2: "-10" }), 3);
    expect(errors.plot_area_m2).toBeTruthy();
  });

  it("rejects an out-of-range orientation", () => {
    expect(validateForm(validForm({ orientation_deg: "400" }), 3).orientation_deg).toBeTruthy();
    expect(validateForm(validForm({ orientation_deg: "-1" }), 3).orientation_deg).toBeTruthy();
  });

  it("accepts the orientation boundary values", () => {
    expect(validateForm(validForm({ orientation_deg: "0" }), 3)).toEqual({});
    expect(validateForm(validForm({ orientation_deg: "360" }), 3)).toEqual({});
  });

  it("rejects an implausible construction year", () => {
    expect(validateForm(validForm({ construction_year: "1800" }), 3).construction_year).toBeTruthy();
  });

  it("rejects an out-of-range latitude", () => {
    expect(validateForm(validForm({ latitude: "95" }), 3).latitude).toBeTruthy();
  });

  it("rejects an out-of-range longitude", () => {
    expect(validateForm(validForm({ longitude: "181" }), 3).longitude).toBeTruthy();
  });

  it("does not validate later steps when asked about an earlier one", () => {
    // Step 1 validation must not complain about a bad floor count.
    const errors = validateForm(validForm({ num_floors: "999" }), 1);
    expect(Object.keys(errors)).toHaveLength(0);
  });
});

describe("firstInvalidStep", () => {
  it("returns null for a valid form", () => {
    expect(firstInvalidStep(validForm())).toBeNull();
  });

  it("returns the first step that fails", () => {
    expect(firstInvalidStep(validForm({ name: "" }))).toBe(1);
    expect(firstInvalidStep(validForm({ num_floors: "0" }))).toBe(2);
  });

  it("returns 1 when both step 1 and step 2 are invalid", () => {
    expect(firstInvalidStep(validForm({ name: "", num_floors: "0" }))).toBe(1);
  });
});

describe("buildPayload", () => {
  it("includes the required fields with correct types", () => {
    const payload = buildPayload(validForm({ num_floors: "6", floor_to_floor_height_m: "3.0" }));
    expect(payload).toMatchObject({
      name: "Dhaka Residential Block A",
      city: "Dhaka",
      building_type: "Residential",
      num_floors: 6,
      floor_to_floor_height_m: 3.0,
    });
    expect(typeof payload.num_floors).toBe("number");
    expect(typeof payload.floor_to_floor_height_m).toBe("number");
  });

  it("omits blank optional fields instead of sending null or 0", () => {
    const payload = buildPayload(validForm());
    for (const key of [
      "building_name",
      "plot_area_m2",
      "building_footprint_m2",
      "construction_year",
      "structural_system",
      "latitude",
      "longitude",
    ]) {
      expect(payload).not.toHaveProperty(key);
    }
  });

  it("includes optional fields the user actually filled in", () => {
    const payload = buildPayload(
      validForm({
        building_name: "Block A",
        plot_area_m2: "500",
        building_footprint_m2: "200",
        construction_year: "2020",
        structural_system: "Frame",
        latitude: "23.8103",
        longitude: "90.4125",
      })
    );
    expect(payload).toMatchObject({
      building_name: "Block A",
      plot_area_m2: 500,
      building_footprint_m2: 200,
      construction_year: 2020,
      structural_system: "Frame",
      latitude: 23.8103,
      longitude: 90.4125,
    });
  });

  it("defaults orientation to 0 when left blank", () => {
    const payload = buildPayload(validForm({ orientation_deg: "" }));
    expect(payload.orientation_deg).toBe(0);
  });

  it("preserves a user-entered orientation", () => {
    const payload = buildPayload(validForm({ orientation_deg: "180" }));
    expect(payload.orientation_deg).toBe(180);
  });

  it("trims whitespace from text fields", () => {
    const payload = buildPayload(validForm({ name: "  Block A  ", city: "  Dhaka  " }));
    expect(payload.name).toBe("Block A");
    expect(payload.city).toBe("Dhaka");
  });
});

describe("reviewRows", () => {
  it("shows the values the user typed, not placeholders", () => {
    const rows = reviewRows(
      validForm({
        name: "My Tower",
        city: "Chattogram",
        building_type: "Mixed-use",
        num_floors: "12",
        floor_to_floor_height_m: "3.5",
        plot_area_m2: "800",
      })
    );

    const byLabel = Object.fromEntries(rows.map((r) => [r.label, r.value]));

    expect(byLabel["Project"]).toBe("My Tower");
    expect(byLabel["City"]).toBe("Chattogram");
    expect(byLabel["Building Type"]).toBe("Mixed-use");
    expect(byLabel["Floors"]).toBe("12");
    expect(byLabel["Floor Height"]).toBe("3.5 m");
    expect(byLabel["Plot Area"]).toBe("800 m²");
  });

  it("marks omitted optional fields as not provided", () => {
    const rows = reviewRows(validForm());
    const byLabel = Object.fromEntries(rows.map((r) => [r.label, r.value]));
    expect(byLabel["Building Name"]).toBe("Not provided");
    expect(byLabel["Plot Area"]).toBe("Not provided");
    expect(byLabel["Structural System"]).toMatch(/will be flagged/i);
  });

  it("labels a blank orientation as the default North", () => {
    const rows = reviewRows(validForm({ orientation_deg: "" }));
    const byLabel = Object.fromEntries(rows.map((r) => [r.label, r.value]));
    expect(byLabel["Orientation"]).toBe("0° (default North)");
  });

  it("shows an entered orientation verbatim", () => {
    const rows = reviewRows(validForm({ orientation_deg: "270" }));
    const byLabel = Object.fromEntries(rows.map((r) => [r.label, r.value]));
    expect(byLabel["Orientation"]).toBe("270°");
  });

  it("says floor area is derived when left blank", () => {
    const rows = reviewRows(validForm({ total_floor_area: "" }));
    const byLabel = Object.fromEntries(rows.map((r) => [r.label, r.value]));
    expect(byLabel["Total Floor Area"]).toBe("Derived from rooms");
  });

  it("includes every expected row exactly once", () => {
    const rows = reviewRows(validForm());
    const labels = rows.map((r) => r.label);
    expect(new Set(labels).size).toBe(labels.length);
    expect(labels).toContain("Project");
    expect(labels).toContain("Coordinates");
  });
});

describe("round trip: form -> payload -> review", () => {
  it("keeps the review text and the payload consistent", () => {
    const form = validForm({
      name: "Consistency Check",
      num_floors: "8",
      floor_to_floor_height_m: "3.2",
    });

    const payload = buildPayload(form);
    const rows = reviewRows(form);
    const byLabel = Object.fromEntries(rows.map((r) => [r.label, r.value]));

    expect(payload.name).toBe("Consistency Check");
    expect(byLabel["Project"]).toBe(String(payload.name));

    expect(payload.num_floors).toBe(8);
    expect(byLabel["Floors"]).toBe("8");

    expect(payload.floor_to_floor_height_m).toBe(3.2);
    expect(byLabel["Floor Height"]).toBe("3.2 m");
  });
});