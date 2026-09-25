const { chromium } = require('@playwright/test');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: '.auth/bo-8082.json', baseURL: 'http://localhost:8082', locale: 'fr-FR' });
  const page = await ctx.newPage();
  await page.goto('/admin-dev/');
  await page.goto(await page.locator('a[href*="international/translations"]').first().getAttribute('href'));
  await page.selectOption('#form_translation_type', 'themes');
  await page.selectOption('#form_theme', 'classic');
  await page.selectOption('#form_language', 'fr');
  const first = page.waitForResponse(r => /\/api\/translations\/fr-FR\//.test(r.url()));
  await Promise.all([page.waitForNavigation(), page.getByRole('button', { name: 'Modifier' }).click()]);
  const u = (await first).url(); const tr = await page.request.get(u.replace(/fr-FR\/[^/?]+\/classic/, "tree/fr/themes/classic")); require("fs").writeFileSync(process.argv[2]+"-tree.json", await tr.text());
  for (const d of process.argv.slice(3)) {
    const url = u.replace(/fr-FR\/[^/]+\/classic/, `fr-FR/${d}/classic`);
    const r = await page.request.get(url);
    const j = await r.json().catch(async () => ({ raw: (await r.text()).slice(0, 300) }));
    require('fs').writeFileSync(`${process.argv[2]}-${d}.json`, JSON.stringify(j, null, 1));
    console.log(d, r.status(), j.data ? j.data.length : JSON.stringify(j).slice(0,300));
  }
  await b.close();
})();
