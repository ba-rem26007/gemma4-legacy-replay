const { chromium } = require('@playwright/test');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: '.auth/bo-8082.json', baseURL: 'http://localhost:8082', locale: 'fr-FR' });
  const page = await ctx.newPage();
  page.on('request', r => { if (/emailHTML|EmailHTML/i.test(r.url())) console.log('REQ', r.url()); });
  await page.goto('/admin-dev/');
  await page.goto(await page.locator('a[href*="international/translations"]').first().getAttribute('href'));
  await page.selectOption('#form_translation_type', 'mails');
  await page.selectOption('#form_email_content_type', 'body');
  console.log(await page.locator('form').first().innerHTML().then(h => h.match(/<select[^>]*>/g)));
  await page.selectOption('#form_theme', 'classic');
  await page.selectOption('#form_language', 'fr').catch(e=>console.log('lang', e.message));
  await Promise.all([page.waitForNavigation(), page.getByRole('button', { name: 'Modifier' }).click()]);
  console.log(page.url());
  require('fs').writeFileSync(process.argv[2], await page.content());
  await b.close();
})();
