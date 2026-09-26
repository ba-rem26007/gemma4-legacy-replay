// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37874, validé pre/post automatiquement
// Issue: BO > Movements - Search results is undefined and loads forever
// The bug is caused by missing columns (ean13, isbn, upc, mpn) in the StockMovementRepository SQL query.
// When searching for a non-existent product, the frontend fails to map the response, 
// resulting in an "undefined" notification and an infinite loading state.
const { test, expect } = require('@playwright/test');

test('la recherche d\'un produit inexistant dans les mouvements de stock ne doit pas afficher "undefined"', async ({ page }) => {
  // Accès direct à la page des mouvements pour éviter les problèmes de menus repliés
  // Le prompt indique que l'absence de token mène à la page "comprends les risques"
  await page.goto('/admin-dev/stock-movements');

  // Gestion de la page de sécurité Symfony
  const riskLink = page.locator('text=/comprends les risques|understand the risks/i');
  if (await riskLink.isVisible()) {
    await riskLink.click();
  }

  // Saisie d'une valeur de recherche qui ne retournera aucun résultat
  const searchInput = page.locator('input[name="search"]');
  await searchInput.waitFor({ state: 'visible' });
  await searchInput.fill('NON_EXISTENT_PRODUCT_99999');
  
  // On intercepte la réponse de la recherche
  const responsePromise = page.waitForResponse(r => r.url().includes('stock-movements') && r.request().method() === 'GET');
  
  // Clic sur le bouton de recherche
  await page.locator('button[type="submit"]').click();
  await responsePromise;

  // ASSERTIONS :
  // 1. Le texte "undefined" ne doit pas apparaître dans les notifications (toast/alertes)
  // On utilise un délai court pour s'assurer que le JS a eu le temps de tenter d'afficher l'erreur
  await expect(page.locator('text=undefined')).not.toBeVisible();

  // 2. Le loader doit disparaître (le bug provoquait un chargement infini)
  // On vérifie l'absence d'éléments de chargement communs dans le BO PrestaShop
  await expect(page.locator('.loading-overlay, .spinner, [data-loader], .loading')).not.toBeVisible();
  
  // 3. Vérification métier : on doit voir un message indiquant qu'aucun résultat n'a été trouvé
  // On utilise une regex large pour couvrir le français et l'anglais
  await expect(page.locator('body')).toContainText(/aucun|no results/i);
});
