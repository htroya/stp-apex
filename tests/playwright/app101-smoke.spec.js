const { test, expect } = require('@playwright/test');

const appBaseUrl =
  process.env.APP_URL ||
  'https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/r/stp/test101';

test('login page for app 101 loads', async ({ page }) => {
  await page.goto(`${appBaseUrl}/login`, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#P9999_USERNAME')).toBeVisible();
  await expect(page.locator('#P9999_PASSWORD')).toBeVisible();
  await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
});

test('optional authenticated smoke for app 101', async ({ page }) => {
  test.skip(
    !process.env.APP_USERNAME || !process.env.APP_PASSWORD,
    'Set APP_USERNAME and APP_PASSWORD to run the authenticated smoke test.',
  );

  await page.goto(`${appBaseUrl}/login`, { waitUntil: 'domcontentloaded' });
  await page.fill('#P9999_USERNAME', process.env.APP_USERNAME);
  await page.fill('#P9999_PASSWORD', process.env.APP_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();

  await page.waitForLoadState('networkidle');
  await expect(page).toHaveURL(/\/home|f\?p=/);
  await expect(page.locator('body')).toContainText(/test101/i);
});
