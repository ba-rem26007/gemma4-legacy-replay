const { chromium } = require('@playwright/test');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: '/home/elrems/kaggle/bench/replay/.auth/bo-8083.json', baseURL: 'http://localhost:8083' });
  const page = await ctx.newPage();
  await page.goto(process.argv[2]);
  if (page.url().includes('security/compromised')) await page.locator('a:has-text("Oui")').first().click();
  await page.waitForLoadState();
  console.log(page.url());
  if (process.argv[4]) console.log((await page.locator(process.argv[5]||'body').innerText()).slice(0, +process.argv[4]));
  const hrefs = await page.$$eval('a', as => as.map(a => a.getAttribute('href')).filter(Boolean));
  console.log(hrefs.filter(h => new RegExp(process.argv[3] || '.').test(h)).slice(0, 60).join('\n'));
  await b.close();
})();
