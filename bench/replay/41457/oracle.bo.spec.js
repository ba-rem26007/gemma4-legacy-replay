// Issue #41457 : avec « Ajouter l'année au numéro de facture » activé, le nom du fichier PDF
// de facture ne contient plus que l'année (ex. 2026.pdf) car le numéro formaté contient un « / ».
// setup.sql crée la facture n° 7706 de 2026 (préfixe #IN, année après le numéro).
// Vérifie que le nom de fichier proposé au téléchargement contient préfixe + numéro + année,
// sans « / » (attendu : #IN007706-2026.pdf).
const { test, expect } = require('@playwright/test');

test('nom du PDF de facture complet quand l’année est ajoutée', async ({ page }) => {
  // Lien legacy sans jeton : la page « jeton invalide » propose le lien signé, qui déclenche le téléchargement
  await page.goto('/admin-dev/index.php?controller=AdminPdf&submitAction=generateInvoicePDF&id_order_invoice=41457');
  await expect(page).toHaveURL(/security\/compromised/);
  const dl = page.waitForEvent('download');
  await page.locator('a:has-text("Oui")').first().click();
  const download = await dl;
  const name = download.suggestedFilename();
  expect(name).toContain('007706');
  expect(name).toContain('IN');
  expect(name).toMatch(/2026\.pdf$/);
});
