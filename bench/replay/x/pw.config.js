const { defineConfig } = require('@playwright/test');
module.exports = defineConfig({ testDir: '.', timeout: 90000, reporter: 'list',
  outputDir: '/tmp/claude-1000/-home-elrems-kaggle/144dfd91-272c-4a17-b325-fc1a6d449767/scratchpad/tr',
  use: { baseURL: 'http://localhost:8081', locale: 'fr-FR',  },
  projects: [{ name: 'x', testMatch: /explore.*\.spec\.js/ }] });
