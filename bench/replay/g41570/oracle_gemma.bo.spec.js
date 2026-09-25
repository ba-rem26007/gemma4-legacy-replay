// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #41570, validé pre/post automatiquement
// Issue: The position column (drag-and-drop handle) is missing in the Features list.
// The fix changes the default 'orderBy' from 'name' to 'position' in FeatureFilters.php.
// In PrestaShop Symfony grids, the position column is only rendered when the grid is ordered by position.
const { test, expect } = require('@playwright/test');

test('the features list should display the position column for reordering', async ({ page }) => {
  // 1. Go to Back-Office home to establish session and handle security page
  await page.goto('/admin-dev/');
  
  const riskButton = page.locator('text=/comprends les risques|understand the risks/i');
  if (await riskButton.isVisible()) {
    await riskButton.click();
  }

  // 2. Navigate to Catalog -> Features
  // We look for the link in the menu to ensure we have the correct Symfony token
  const featuresLink = page.locator('a[href*="catalog/features"]');
  await featuresLink.click();

  // 3. Verify the presence of the position column
  // The position column in Symfony grids has the class 'grid-position'
  // It is absent when 'orderBy' is 'name' and present when 'orderBy' is 'position'
  const positionHeader = page.locator('th.grid-position');
  await expect(positionHeader).toBeVisible();

  // 4. Verify that the table rows contain the drag handle cells
  const positionCells = page.locator('td.grid-position');
  await expect(positionCells.first()).toBeVisible();
});
