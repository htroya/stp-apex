const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/playwright',
  timeout: 30_000,
  use: {
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
});
