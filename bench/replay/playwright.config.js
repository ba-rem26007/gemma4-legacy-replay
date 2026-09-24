// Tests de replay : un dossier par bug (<pr>/), lancés contre la stack de bench/env
// Les specs *.bo.spec.js utilisent la session BO créée par auth.setup.js
const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({
  testDir: '.',
  timeout: 60_000,
  retries: 0,
  reporter: [['list'], ['json', { outputFile: 'results.json' }]],
  use: {
    baseURL: `http://localhost:${process.env.PS_PORT || 8081}`,
    locale: 'fr-FR',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'setup', testMatch: 'auth.setup.js' },
    { name: 'fo', testMatch: '*/replay.spec.js', testIgnore: '*/*.bo.spec.js' },
    { name: 'bo', testMatch: '*/*.bo.spec.js', dependencies: ['setup'], use: { storageState: '.auth/bo.json' } },
  ],
});
