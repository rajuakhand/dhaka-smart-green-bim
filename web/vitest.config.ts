import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // Only unit tests. Playwright specs live in tests/e2e and are run
    // separately with `npx playwright test`.
    include: ["tests/**/*.test.ts", "tests/**/*.test.tsx"],
    exclude: ["tests/e2e/**", "node_modules/**"],
    environment: "node",
  },
});