import { test, expect } from "@playwright/test";

test("home page loads", async ({ page }) => {
  await page.goto("/");
  // App root mounts — check the #root div has content
  await expect(page.locator("#root")).not.toBeEmpty();
});
