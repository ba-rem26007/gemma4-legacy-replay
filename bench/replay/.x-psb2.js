const { chromium } = require('@playwright/test');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: '.auth/bo-8082.json', baseURL: 'http://localhost:8082', locale: 'fr-FR' });
  const page = await ctx.newPage();
  page.on('response', async r => { if (/\/api\/translations/.test(r.url())) console.log('RESP', r.status(), r.url().slice(0,200)); });
  await page.goto('/admin-dev/');
  await page.goto(await page.locator('a[href*="international/translations"]').first().getAttribute('href'));
  await page.selectOption('#form_translation_type', 'themes');
  await page.selectOption('#form_theme', 'classic').catch(e=>console.log(e.message));
  await page.selectOption('#form_language', 'fr');
  await Promise.all([page.waitForNavigation(), page.getByRole('button', { name: 'Modifier' }).click()]);
  console.log(page.url());
  await page.waitForTimeout(4000);
  await page.getByText('Checkout', { exact: false }).first().click().catch(e=>console.log('click', e.message));
  await page.waitForTimeout(4000);
  require('fs').writeFileSync(process.argv[2], await page.content());
  await b.close();
})();
