const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './.generated-tests',
  reporter: [
    ['list'],
    ['html', {
      outputFolder: 'playwright-report',
      open: 'never'
    }]
  ],
  use: {
    headless: true,
  },
});
