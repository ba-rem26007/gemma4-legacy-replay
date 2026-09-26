// Test de reproduction écrit par Gemma (gemma-4-31b-it) à partir du TICKET SEUL — PR #41675
const { test, expect } = require('@playwright/test');
// Issue: HTMLPurifier through twig extension is not adhering to cache dir config.
// It writes to vendor/ezyang/htmlpurifier/library/HTMLPurifier/DefinitionCache 
// instead of var/cache/purifier.

const { execSync } = require('child_process');

const PROJ = 'psbench' + ((process.env.PS_PORT || '8081') === '8081' ? '' : String(Number(process.env.PS_PORT) - 8080));

// Robustly find the PHP/Web container ID to avoid "No such container" errors
const getContainerId = () => {
  try {
    // Find container that matches the project name and is NOT the db container
    return execSync(`docker ps -q -f name=${PROJ} | grep -v db`).toString().trim();
  } catch (e) {
    // Fallback to a common name if grep fails
    return `${PROJ}-php-1`;
  }
};

const containerId = getContainerId();
const shell = cmd => execSync(`docker exec ${containerId} ${cmd}`).toString().trim();

test('HTMLPurifier cache should be in var/cache/purifier, not in vendor', async ({ page }) => {
  const vendorCachePath = '/var/www/html/vendor/ezyang/htmlpurifier/library/HTMLPurifier/DefinitionCache';
  const correctCachePath = '/var/www/html/var/cache/purifier';

  // 1. Clean up and ensure directories exist
  // We remove the directory and recreate it to ensure a completely empty state
  shell(`rm -rf ${correctCachePath} && mkdir -p ${correctCachePath}`);
  shell(`rm -rf ${vendorCachePath} && mkdir -p ${vendorCachePath}`);

  // 2. Trigger the HTMLPurifier via a Symfony-based page
  await page.goto('/admin-dev/');
  if (page.url().includes('security/compromised')) {
    await page.locator('a:has-text("Oui")').first().click();
  }
  
  // Navigate to a product page in BO (which renders purified content via Twig)
  await page.goto('/admin-dev/index.php?controller=AdminProducts');
  // Click on the first product in the list to enter the product edit page
  await page.locator('.product-grid-item a, .grid-item a').first().click();
  await page.waitForLoadState('networkidle');

  // 3. Check for files in the wrong directory (vendor)
  // We use 'find' and count files. If the directory is empty, find returns nothing.
  const vendorFiles = shell(`find ${vendorCachePath} -type f`);
  const vendorFilesCount = vendorFiles ? vendorFiles.split('\n').filter(Boolean).length : 0;
  
  // 4. Check for files in the correct directory (var/cache)
  const correctFiles = shell(`find ${correctCachePath} -type f`);
  const correctFilesCount = correctFiles ? correctFiles.split('\n').filter(Boolean).length : 0;

  // The test fails if files are found in the vendor directory (Bug present)
  // The test passes if vendor is empty and files are in var/cache (Bug fixed)
  expect(vendorFilesCount, 'No cache files should be created in the vendor directory').toBe(0);
  expect(correctFilesCount, 'Cache files should be created in var/cache/purifier').toBeGreaterThan(0);
});
