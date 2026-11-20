import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config for DhakaSmart UI tests.
 *
 * The dev server is NOT started here on purpose: tests are pointed at an
 * already-running instance via BASE_URL so they can be run against staging
 * or production too.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: process.env.BASE_URL ?? "http://localhost:3000",
    trace: "retain-on-failure",
    ...devices["Desktop Chrome"],
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});