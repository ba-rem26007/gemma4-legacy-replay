// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37944, validé pre/post automatiquement
// Issue: MaterialChoiceTableType does not render help text.
// The "Group access" (Accès groupe) field in the Category edit page uses this type.
// We verify that the help text associated with this field is rendered in the DOM.
const { test, expect } = require('@playwright/test');

test('le texte d\'aide du champ Accès groupe est affiché dans la modification d\'une catégorie', async ({ page }) => {
  await page.goto('/admin-dev/');

  // Gestion de la page de sécurité Symfony (token)
  const riskButton = page.getByText(/comprends les risques|understand the risks/i);
  if (await riskButton.isVisible()) {
    await riskButton.click();
  }

  // Navigation vers Catalogue > Catégories
  // On cherche le lien qui contient "categories" dans l'URL pour éviter les libellés fragiles
  await page.click('a[href*="categories"]');

  // On clique sur "Modifier" pour la première catégorie de la liste
  await page.click('text=Modifier');

  // Le champ "Accès groupe" est un MaterialChoiceTableType.
  // Le texte d'aide attendu est : "Sélectionnez les groupes de clients qui peuvent accéder à cette catégorie"
  // On utilise une regex large pour être robuste aux changements mineurs de traduction.
  const helpText = page.locator('div.help-block, p.help-block, .form-text').filter({ hasText: /S\w+lez les groupes de clients/i });
  
  // Avant le correctif, le bloc {{ block('form_help') }} était absent du template Twig, 
  // donc l'élément n'est pas rendu dans le DOM.
  await expect(helpText).toBeVisible();
});
