// Oracle écrit par Gemma (gemma-4-31b-it) pour PR #37996, validé pre/post automatiquement
// Issue: Setting an inactive parent tab (like "More") as the default page causes a crash.
// The fix prevents inactive tabs from appearing in the "Default page" dropdown in the employee profile,
// even if they have active children.
const { test, expect } = require('@playwright/test');

test('inactive parent tabs should not be selectable as the default page', async ({ page }) => {
  // Go to the employee profile page
  await page.goto('/admin-dev/employee/profile');

  // Handle the Symfony security warning page if it appears
  const securityWarning = page.getByText(/comprends les risques|understand the risks/i);
  if (await securityWarning.isVisible()) {
    await securityWarning.click();
  }

  // The "Default page" is a select dropdown.
  // In Symfony forms, the name is typically 'employee[default_page]'
  const defaultPageSelect = page.locator('select[name*="default_page"]');
  await expect(defaultPageSelect).toBeVisible();

  // Before the fix, the tab with id 9999 (inactive but has children) was listed.
  // After the fix, it must be absent from the options.
  // We check for the specific value '9999' in the options.
  const option = defaultPageSelect.locator('option[value="9999"]');
  await expect(option).toHaveCount(0);
});
