const { test } = require('@playwright/test');
test('x', async ({ page }) => { await require('./login')(page);
  await page.goto('/admin-dev/');
  console.log('URL', page.url(), await page.locator('a[href*="attribute-groups"]').count());
});
