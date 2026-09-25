const { chromium } = require('@playwright/test');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: '.auth/bo-8082.json', baseURL: 'http://localhost:8082', locale: 'fr-FR' });
  const page = await ctx.newPage();
  page.on('request', r => { if (r.method()==='POST') console.log('POST', r.url().slice(0,150)); });
  page.on('response', async r => { if (r.request().method()==='POST') console.log('RESP', r.status(), (await r.text().catch(()=>'')).slice(0,300)); });
  await page.goto('/admin-dev/');
  await page.goto(await page.locator('a[href*="improve/modules/manage"]').first().getAttribute('href'));
  console.log(await page.locator('.dz-hidden-input').count());
  await page.locator('#page-header-desc-configuration-add_module').click().catch(e=>console.log('btn',e.message.slice(0,100)));
  await page.waitForTimeout(1000);
  await page.locator('.dz-hidden-input').first().setInputFiles('40070/benchcarrierhook.zip');
  await page.waitForTimeout(8000);
  console.log(await page.locator('.module-import-success, .module-import-failure').allInnerTexts());
  await b.close();
})();
