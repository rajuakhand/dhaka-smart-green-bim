/**
 * End-to-end test for the Create New Project wizard.
 *
 * Proves that values entered in steps 1-3 appear verbatim in step 4 and are
 * sent to the API unchanged. This guards against the regression where the
 * review step showed hardcoded placeholders instead of user input.
 *
 * Run against a live dev server:
 *   BASE_URL=http://localhost:3000 npx playwright test
 */
import { test, expect } from "@playwright/test";

const BASE = process.env.BASE_URL ?? "http://localhost:3000";
const API = process.env.API_URL ?? "http://localhost:8000";

const PROJECT_NAME = `E2E Wizard ${Date.now()}`;

test("wizard carries entered values through to review and creates the project", async ({
  page,
  request,
}) => {
  await page.goto(`${BASE}/projects/new`);

  // ---- Step 1: project details ----
  await expect(page.getByText("Step 1 of 4")).toBeVisible();
  await page.getByLabel(/Project Name/i).fill(PROJECT_NAME);
  await page.getByLabel(/^City/i).fill("Chattogram");
  await page.getByLabel(/Building Name/i).fill("Anonymised Block Z");

  await page.getByRole("button", { name: "Next", exact: true }).click();

  // ---- Step 2: building configuration ----
  await expect(page.getByText("Step 2 of 4")).toBeVisible();
  await page.getByLabel(/Building Type/i).selectOption("Mixed-use");
  await page.getByLabel(/Number of Floors/i).fill("12");
  await page.getByLabel(/Floor-to-Floor Height/i).fill("3.5");

  await page.getByRole("button", { name: "Next", exact: true }).click();

  // ---- Step 3: site information ----
  await expect(page.getByText("Step 3 of 4")).toBeVisible();
  await page.getByLabel(/Plot Area/i).fill("800");
  await page.getByLabel(/Building Footprint/i).fill("250");
  await page.getByLabel(/Orientation/i).fill("270");
  await page.getByLabel(/Construction Year/i).fill("2019");
  await page.getByLabel(/Structural System/i).selectOption("Frame");
  await page.getByLabel(/^Latitude/i).fill("22.3569");
  await page.getByLabel(/^Longitude/i).fill("91.7832");

  await page.getByRole("button", { name: "Next", exact: true }).click();

  // ---- Step 4: review must echo exactly what was entered ----
  await expect(page.getByText("Step 4 of 4")).toBeVisible();

  const review = page.locator(".bg-slate-50").first();
  await expect(review).toContainText(PROJECT_NAME);
  await expect(review).toContainText("Chattogram");
  await expect(review).toContainText("Anonymised Block Z");
  await expect(review).toContainText("Mixed-use");
  await expect(review).toContainText("12");
  await expect(review).toContainText("3.5 m");
  await expect(review).toContainText("800 m²");
  await expect(review).toContainText("250 m²");
  await expect(review).toContainText("270°");
  await expect(review).toContainText("2019");
  await expect(review).toContainText("Frame");
  await expect(review).toContainText("22.3569");
  await expect(review).toContainText("91.7832");

  // ---- Create and verify the server received the same values ----
  const created = page.waitForResponse(
    (r) => r.url().includes("/api/v1/projects") && r.request().method() === "POST"
  );
  await page.getByRole("button", { name: "Create Project", exact: true }).click();

  const res = await created;
  expect(res.status()).toBe(201);

  const body = await res.json();
  expect(body.name).toBe(PROJECT_NAME);
  expect(body.city).toBe("Chattogram");
  expect(body.building_name).toBe("Anonymised Block Z");
  expect(body.building_type).toBe("Mixed-use");
  expect(body.num_floors).toBe(12);
  expect(body.floor_to_floor_height_m).toBe(3.5);
  expect(body.plot_area_m2).toBe(800);
  expect(body.building_footprint_m2).toBe(250);
  expect(body.orientation_deg).toBe(270);
  expect(body.construction_year).toBe(2019);
  expect(body.structural_system).toBe("Frame");

  // Landed on the new project page
  await page.waitForURL(`**/projects/${body.id}`);

  // Clean up
  await request.delete(`${API}/api/v1/projects/${body.id}`);
});

test("step 1 blocks advancing when the project name is missing", async ({ page }) => {
  await page.goto(`${BASE}/projects/new`);

  await page.getByLabel(/^City/i).fill("Dhaka");
  await page.getByRole("button", { name: "Next", exact: true }).click();

  await expect(page.getByText("Step 1 of 4")).toBeVisible();
  await expect(page.getByText(/Project name is required/i)).toBeVisible();
});

test("footprint larger than the plot is rejected before submission", async ({ page }) => {
  await page.goto(`${BASE}/projects/new`);

  await page.getByLabel(/Project Name/i).fill("Geometry Guard");
  await page.getByLabel(/^City/i).fill("Dhaka");
  await page.getByRole("button", { name: "Next", exact: true }).click();

  await page.getByRole("button", { name: "Next", exact: true }).click();

  await page.getByLabel(/Plot Area/i).fill("400");
  await page.getByLabel(/Building Footprint/i).fill("900");
  await page.getByRole("button", { name: "Next", exact: true }).click();

  await expect(page.getByText(/cannot exceed the plot area/i)).toBeVisible();
  await expect(page.getByText("Step 3 of 4")).toBeVisible();
});