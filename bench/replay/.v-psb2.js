const { chromium } = require('@playwright/test');
const zlib = require('zlib');
function png(w, h) { // PNG RGB uni
  const crcT = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; crcT[n] = c >>> 0; }
  const crc = b => { let c = 0xffffffff; for (const x of b) c = crcT[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
  const chunk = (t, d) => { const l = Buffer.alloc(4); l.writeUInt32BE(d.length); const td = Buffer.concat([Buffer.from(t), d]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); };
  const ih = Buffer.alloc(13); ih.writeUInt32BE(w, 0); ih.writeUInt32BE(h, 4); ih[8] = 8; ih[9] = 2;
  const raw = Buffer.alloc((w * 3 + 1) * h); for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) { const o = y * (w * 3 + 1) + 1 + x * 3; raw[o] = 200; raw[o + 1] = 30; raw[o + 2] = 30; }
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ih), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
}
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ storageState: '.auth/bo-8082.json', baseURL: 'http://localhost:8082', locale: 'fr-FR' });
  const page = await ctx.newPage();
  await page.goto('/admin-dev/');
  const u = await page.locator('a[href*="improve/design/themes/"]').first().getAttribute('href');
  await page.goto(u + '&setShopContext=' + process.argv[2]);
  console.log(await page.locator('.shop-list, #shop-list, .header-multishop').first().innerText().catch(()=>'?'));
  await page.locator('#form_header_logo').setInputFiles({ name: 'bench.png', mimeType: 'image/png', buffer: png(40, 20) });
  const btn = page.locator('#form_header_logo').locator('xpath=ancestor::form').locator('button.btn-primary').first();
  const [resp] = await Promise.all([page.waitForNavigation(), btn.click()]);
  console.log(resp && resp.status(), page.url().slice(0,120));
  console.log((await page.locator('.alert').allInnerTexts()).map(s=>s.trim().slice(0,300)).filter(Boolean));
  await b.close();
})();
