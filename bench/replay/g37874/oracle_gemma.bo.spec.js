// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37874, validé pre/post automatiquement
// Issue: BO > Movements - Search results is undefined and loads forever
// When searching for a non-existent product, the missing EAN13/ISBN/UPC/MPN fields 
// in the SQL query cause a JS crash in the frontend, leading to an "undefined" 
// notification and an infinite loading spinner.
const { test, expect } = require('@playwright/test');

test('la recherche d\'un produit inexistant dans les mouvements de stock ne crash pas', async ({ page }) => {
  // Navigation vers le Back Office
  await page.goto('/admin-dev/');

  // Gestion de la page de sécurité Symfony (jeton/risques)
  const riskBtn = page.getByText(/comprends les risques|understand the risks/i);
  if (await riskBtn.isVisible()) {
    await riskBtn.click();
  }

  // Accès à la page Mouvements de stock
  // On récupère le lien via le menu pour garantir la validité du token Symfony
  const movementsLink = await page.locator('a[href*="stock-movements"]').getAttribute('href');
  await page.goto(movementsLink);

  // Recherche d'un produit qui n'existe absolument pas
  const searchInput = page.locator('input[name="search_product"]');
  await searchInput.fill('NON_EXISTENT_PRODUCT_999999');
  await page.keyboard.press('Enter');

  // Le bug se manifeste par une notification "undefined" et un spinner infini.
  // On attend que la requête réseau soit terminée.
  await page.waitForLoadState('networkidle');

  // Assertion 1 : Le texte "undefined" ne doit pas apparaître dans les notifications/alertes
  await expect(page.locator('body')).not.toContainText('undefined');

  // Assertion 2 : Le masque de chargement (loading mask) doit avoir disparu
  // Dans PrestaShop BO, le spinner est généralement géré par une classe .loading-mask ou similaire
  await expect(page.locator('.loading-mask')).not.toBeVisible();

  // Assertion 3 : On vérifie que la page a bien affiché le résultat (même vide) 
  // en vérifiant la présence du tableau ou d'un message de résultat.
  await expect(page.locator('table, .no-results')).toBeVisible();
});
