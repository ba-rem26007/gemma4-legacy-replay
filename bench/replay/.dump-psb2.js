// usage: node dump.js <path-regex-replacement from orders href> 
const { chromium } = require('@playwright/test');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: '/home/elrems/kaggle/bench/replay/.auth/bo-8082.json', baseURL: 'http://localhost:8082', locale: 'fr-FR' });
  const page = await ctx.newPage();
  await page.goto('/admin-dev/');
  const sel = process.argv[2], from = process.argv[3], to = process.argv[4];
  let href = await page.locator(`a[href*="${sel}"]`).first().getAttribute('href');
  if (from) href = href.replace(new RegExp(from), to);
  console.log('URL', href);
  await page.goto(href);
  require('fs').writeFileSync(process.argv[5] || '/tmp/claude-1000/-home-elrems-kaggle/144dfd91-272c-4a17-b325-fc1a6d449767/scratchpad/psb2/page.html', await page.content());
  console.log(page.url(), await page.title());
  await b.close();
})();
