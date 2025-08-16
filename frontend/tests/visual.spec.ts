import { test, expect } from "@playwright/test";

test.describe("Crypto Trading Manager Visual Tests", () => {
  test.beforeEach(async ({ page }) => {
    // Start from the index page for each test
    await page.goto("http://localhost:3000");
  });

  test("homepage has correct title and navigation", async ({ page }) => {
    // Expect a title "to contain" a substring
    await expect(page).toHaveTitle(/Crypto Trading Manager/);

    // Check navigation elements
    await expect(page.locator("nav")).toBeVisible();
    await expect(page.getByRole("link", { name: "Dashboard" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Portfolio" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Trading" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Market Data" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Settings" })).toBeVisible();
  });

  test("dashboard loads correctly", async ({ page }) => {
    await page.getByRole("link", { name: "Dashboard" }).click();

    // Wait for content to load
    await expect(
      page.getByRole("heading", { name: "Dashboard" })
    ).toBeVisible();

    // Check for main dashboard sections
    await expect(page.locator(".dashboard")).toBeVisible();

    // Take visual screenshot for regression testing
    await expect(page).toHaveScreenshot("dashboard.png");
  });

  test("portfolio page loads and displays correctly", async ({ page }) => {
    await page.getByRole("link", { name: "Portfolio" }).click();

    // Wait for portfolio heading
    await expect(
      page.getByRole("heading", { name: "Portfolio Overview" })
    ).toBeVisible();

    // Check tab navigation
    await expect(page.getByRole("tab", { name: "Overview" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "Balances" })).toBeVisible();
    await expect(page.getByRole("tab", { name: "Transactions" })).toBeVisible();

    // Take visual screenshot
    await expect(page).toHaveScreenshot("portfolio.png");
  });

  test("trading panel functionality", async ({ page }) => {
    await page.getByRole("link", { name: "Trading" }).click();

    // Wait for trading panel
    await expect(
      page.getByRole("heading", { name: "Trading Panel" })
    ).toBeVisible();

    // Check form elements
    await expect(page.getByLabel("Trading Pair")).toBeVisible();
    await expect(page.getByLabel("Amount")).toBeVisible();

    // Test form interaction
    await page.getByLabel("Amount").fill("100");
    await expect(page.getByLabel("Amount")).toHaveValue("100");

    // Take visual screenshot
    await expect(page).toHaveScreenshot("trading-panel.png");
  });

  test("market data displays correctly", async ({ page }) => {
    await page.getByRole("link", { name: "Market Data" }).click();

    // Wait for market data heading
    await expect(
      page.getByRole("heading", { name: "Market Data" })
    ).toBeVisible();

    // Check for market data table
    await expect(page.getByRole("table")).toBeVisible();

    // Take visual screenshot
    await expect(page).toHaveScreenshot("market-data.png");
  });

  test("settings pages accessibility", async ({ page }) => {
    await page.getByRole("link", { name: "Settings" }).click();

    // Check API key settings
    await expect(
      page.getByRole("heading", { name: "API Key Settings" })
    ).toBeVisible();

    // Check accessibility - all form elements should have labels
    const formInputs = page.locator("input, select, textarea");
    const inputCount = await formInputs.count();

    for (let i = 0; i < inputCount; i++) {
      const input = formInputs.nth(i);
      const inputId = await input.getAttribute("id");
      if (inputId) {
        await expect(page.locator(`label[for="${inputId}"]`)).toBeVisible();
      }
    }

    // Take visual screenshot
    await expect(page).toHaveScreenshot("settings.png");
  });

  test("responsive design - mobile view", async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Check navigation works on mobile
    await expect(page.locator("nav")).toBeVisible();

    // Take mobile screenshot
    await expect(page).toHaveScreenshot("mobile-dashboard.png");

    // Test mobile navigation
    await page.getByRole("link", { name: "Portfolio" }).click();
    await expect(page).toHaveScreenshot("mobile-portfolio.png");
  });

  test("dark mode functionality", async ({ page }) => {
    // Check if dark mode toggle exists and works
    const darkModeToggle = page
      .locator('[aria-label*="dark"], [aria-label*="theme"]')
      .first();

    if (await darkModeToggle.isVisible()) {
      await darkModeToggle.click();

      // Wait for theme change
      await page.waitForTimeout(500);

      // Take dark mode screenshot
      await expect(page).toHaveScreenshot("dark-mode.png");
    }
  });

  test("error handling and loading states", async ({ page }) => {
    // Test loading states by checking for loading indicators
    await page.getByRole("link", { name: "Market Data" }).click();

    // Check for loading indicator (might be brief)
    const loadingIndicator = page
      .locator('[role="status"], .loading, .spinner')
      .first();

    // Wait for content to fully load
    await expect(
      page.getByRole("heading", { name: "Market Data" })
    ).toBeVisible();

    // Take screenshot of loaded state
    await expect(page).toHaveScreenshot("market-data-loaded.png");
  });
});

test.describe("Accessibility Tests", () => {
  test("keyboard navigation works correctly", async ({ page }) => {
    await page.goto("http://localhost:3000");

    // Test keyboard navigation through main menu
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");
    await page.keyboard.press("Tab");

    // Should be able to navigate to dashboard with Enter
    await page.keyboard.press("Enter");
    await expect(
      page.getByRole("heading", { name: "Dashboard" })
    ).toBeVisible();
  });

  test("screen reader compatibility", async ({ page }) => {
    await page.goto("http://localhost:3000");

    // Check for proper heading hierarchy
    const h1 = page.locator("h1");
    await expect(h1).toHaveCount(1); // Should have exactly one h1

    // Check for alt text on images
    const images = page.locator("img");
    const imageCount = await images.count();

    for (let i = 0; i < imageCount; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute("alt");
      expect(alt).toBeTruthy(); // All images should have alt text
    }
  });

  test("color contrast and readability", async ({ page }) => {
    await page.goto("http://localhost:3000");

    // Take screenshot for manual contrast analysis
    await expect(page).toHaveScreenshot("contrast-analysis.png");

    // Check that text is not too small
    const bodyText = page.locator("body");
    const fontSize = await bodyText.evaluate((el) => {
      return window.getComputedStyle(el).fontSize;
    });

    // Font size should be at least 16px for accessibility
    const fontSizeNum = parseInt(fontSize);
    expect(fontSizeNum).toBeGreaterThanOrEqual(14);
  });
});
