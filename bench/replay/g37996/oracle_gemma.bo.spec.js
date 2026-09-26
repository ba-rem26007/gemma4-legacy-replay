// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37996, validé pre/post automatiquement
// Issue: An inactive parent tab (which acts as a container for active children) 
// should not be selectable as the default page in the employee profile.
// Before the fix, it was included in the list if it had active children.
const { test, expect } = require('@playwright/test');

test('un onglet parent inactif ne doit pas être disponible dans la liste des pages par défaut', async ({ page }) => {
  // Accès à la page de profil de l'employé
  await page.goto('/admin-dev/employee/profile');

  // Gestion de la page de sécurité Symfony
  const riskBtn = page.getByText(/comprends les risques|understand the risks/i);
  if (await riskBtn.isVisible()) {
    await riskBtn.click();
  }

  // On récupère tous les textes des options de tous les menus déroulants de la page.
  // Le sélecteur "Page par défaut" est un <select>.
  // Avant le correctif : l'onglet est présent car il a des enfants actifs.
  // Après le correctif : l'onglet est exclu car active = 0.
  const options = await page.locator('select option').allInnerTexts();
  
  // On joint tout pour une recherche globale dans les options
  const allOptionsText = options.join(' ');
  
  expect(allOptionsText).not.toContain('TAB_MORE_TEST');
});
