const { chromium } = require('@playwright/test');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: '/home/elrems/kaggle/bench/replay/.auth/bo-8083.json', baseURL: 'http://localhost:8083' });
  const page = await ctx.newPage();
  await page.goto(process.argv[2]);
  if (page.url().includes('security/compromised')) await page.locator('a:has-text("Oui")').first().click();
  await page.waitForLoadState();
  console.log(page.url());
  console.log((await page.locator(process.argv[3]).first().evaluate(e => e.outerHTML)).slice(0, +(process.argv[4]||3000)));
  await b.close();
})();
