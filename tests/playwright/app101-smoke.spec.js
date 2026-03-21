const { test, expect } = require('@playwright/test');

const appBaseUrl =
  process.env.APP_URL ||
  'https://gc6116f6f9e2d14-hhhhhtroya.adb.us-ashburn-1.oraclecloudapps.com/ords/r/stp/test101';
const appUsername = process.env.APP_USERNAME || 'STP';
const appPassword = process.env.APP_PASSWORD;

function extractSession(url) {
  try {
    const parsed = new URL(url);
    const session = parsed.searchParams.get('session');
    if (session) {
      return session;
    }
  } catch {
    // Fall through to the legacy f?p parser below.
  }

  const match = /f\?p=\d+:\d+:(\d+)/i.exec(url);
  return match ? match[1] : null;
}

async function gotoLogin(page) {
  await page.goto(`${appBaseUrl}/login`, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#P9999_USERNAME')).toBeVisible();
  await expect(page.locator('#P9999_PASSWORD')).toBeVisible();
  await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
}

async function login(page) {
  await gotoLogin(page);
  await page.fill('#P9999_USERNAME', appUsername);
  await page.fill('#P9999_PASSWORD', appPassword);

  await Promise.all([
    page.waitForURL(/\/home(?:\?|$)|f\?p=101:1:/i, { timeout: 30_000 }),
    page.getByRole('button', { name: /sign in/i }).click(),
  ]);

  await page.waitForLoadState('domcontentloaded');
  const session = extractSession(page.url());
  expect(session).toBeTruthy();
  return session;
}

async function openAppPage(page, pageAlias, session) {
  await page.goto(`${appBaseUrl}/${pageAlias}?session=${session}`, {
    waitUntil: 'domcontentloaded',
  });
}

async function waitForGridRow(page, value) {
  await page.getByText(value, { exact: true }).waitFor({ timeout: 20_000 });
}

async function hasGridRow(page, value) {
  return page
    .getByText(value, { exact: true })
    .isVisible()
    .catch(() => false);
}

async function expectNoApexError(page) {
  await expect(page.locator('body')).not.toContainText(/ORA-\d{5}|error has occurred|invalid login credentials/i);
}

async function enableGridEditMode(page) {
  await page.getByRole('button', { name: /^Edit$/ }).first().click();
  await expect(page.getByRole('button', { name: /^Save$/ }).first()).toBeVisible();
}

async function updateGridCell(page, currentValue, nextValue) {
  const targetCell = page.locator('.a-GV-cell', { hasText: currentValue }).first();
  const editor = page.getByRole('textbox', { name: 'Name' });
  const updatedCell = page.locator('.a-GV-cell', { hasText: nextValue }).first();

  await targetCell.waitFor({ state: 'visible', timeout: 10_000 });
  await targetCell.click();
  try {
    await editor.waitFor({ state: 'visible', timeout: 2_000 });
  } catch {
    await targetCell.dblclick();
    await editor.waitFor({ state: 'visible', timeout: 10_000 });
  }

  await editor.fill(nextValue);
  await expect(editor).toHaveValue(nextValue);
  await editor.press('Tab');
  await updatedCell.waitFor({ state: 'visible', timeout: 10_000 });
}

async function saveGrid(page) {
  await page.getByRole('button', { name: /^Save$/ }).first().click();
  await expect(page.getByText('Changes saved')).toBeVisible({ timeout: 10_000 });
}

async function openEditableGridFromNavigation(page) {
  const navLink = page.getByRole('treeitem', { name: 'Editable Grid' });
  const menuButton = page.getByRole('button', { name: /main navigation/i });

  if (!(await navLink.isVisible().catch(() => false))) {
    await menuButton.click();
  }

  await expect(navLink).toBeVisible({ timeout: 10_000 });
  await navLink.click();
  await page.waitForURL(/\/editable-grid(?:\?|$)|f\?p=101:2:/i, { timeout: 30_000 });
}

async function ensureGridBaseline(page, stableValue, driftedValue) {
  if (await hasGridRow(page, stableValue)) {
    return;
  }

  if (await hasGridRow(page, driftedValue)) {
    await enableGridEditMode(page);
    await updateGridCell(page, driftedValue, stableValue);
    await saveGrid(page);
    await expectNoApexError(page);
    await page.reload({ waitUntil: 'domcontentloaded' });
    await waitForGridRow(page, stableValue);
    return;
  }

  throw new Error(`No se encontro ni "${stableValue}" ni "${driftedValue}" en el grid.`);
}

test('login page for app 101 loads', async ({ page }) => {
  await gotoLogin(page);
});

test.describe('authenticated pages for app 101', () => {
  test.skip(!appPassword, 'Set APP_PASSWORD to run the authenticated app tests.');

  test('home page loads after signing in', async ({ page }) => {
    await login(page);

    await expect(page).toHaveURL(/\/home(?:\?|$)|f\?p=101:1:/i);
    await expect(page.locator('body')).toContainText(/test|test101/i);
    await expect(page.locator('body')).not.toContainText(/sign in/i);
    await expectNoApexError(page);
  });

  test('interactive grid page loads and supports edit/save on page 2', async ({ page }) => {
    await login(page);
    const originalValue = 'Fila 2';
    const temporaryValue = 'Fila 2 PW';

    await openEditableGridFromNavigation(page);
    await expect(page).toHaveURL(/\/editable-grid\?/i);
    await expect(page.getByRole('heading', { name: 'Editable Grid' })).toBeVisible();
    await expect(page.locator('.a-IG')).toHaveCount(1);
    await expectNoApexError(page);
    await ensureGridBaseline(page, originalValue, temporaryValue);
    await waitForGridRow(page, originalValue);

    await enableGridEditMode(page);
    await updateGridCell(page, originalValue, temporaryValue);
    await saveGrid(page);
    await expectNoApexError(page);

    await page.reload({ waitUntil: 'domcontentloaded' });
    await expectNoApexError(page);
    await waitForGridRow(page, temporaryValue);

    await enableGridEditMode(page);
    await updateGridCell(page, temporaryValue, originalValue);
    await saveGrid(page);
    await expectNoApexError(page);

    await page.reload({ waitUntil: 'domcontentloaded' });
    await expectNoApexError(page);
    await waitForGridRow(page, originalValue);
  });
});
