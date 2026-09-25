const { chromium } = require('@playwright/test');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ baseURL: 'http://localhost:8082', locale: 'fr-FR' });
  const fo = await ctx.newPage();
  await fo.goto('/fr/index.php?id_product=1&id_product_attribute=3&controller=product');
  const added = fo.waitForResponse(r => r.url().includes('cart') && r.request().method() === 'POST');
  await fo.locator('[data-button-action="add-to-cart"]').click();
  await added;
  for (const u of ['/en/', '/fr/', '/en/']) { const r = await fo.goto(u); console.log(u, r.status(), fo.url(), (await fo.content()).length, (await fo.locator('body').innerText()).slice(0,200).replace(/\n/g,' ')); }
  await b.close();
})();
